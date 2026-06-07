import httpx
import asyncio
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

class SplunkClient:
    def __init__(self):
        self.base_url = f"https://{settings.SPLUNK_HOST}:{settings.SPLUNK_PORT}"
        self.hec_url  = f"https://{settings.SPLUNK_HOST}:{settings.SPLUNK_HEC_PORT}"
        self.auth     = (settings.SPLUNK_USERNAME, settings.SPLUNK_PASSWORD)
        logger.info(f"SplunkClient HEC URL: {self.hec_url}")

    async def run_search(self, query: str, earliest: str = "-1h", latest: str = "now") -> list:
        try:
            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                resp = await client.post(
                    f"{self.base_url}/services/search/jobs",
                    auth=self.auth,
                    data={
                        "search":        f"search {query}",
                        "earliest_time": earliest,
                        "latest_time":   latest,
                        "output_mode":   "json"
                    }
                )
                sid = resp.json()["sid"]
                while True:
                    status = await client.get(
                        f"{self.base_url}/services/search/jobs/{sid}",
                        auth=self.auth,
                        params={"output_mode": "json"}
                    )
                    state = status.json()["entry"][0]["content"]["dispatchState"]
                    if state == "DONE":
                        break
                    await asyncio.sleep(0.5)
                results = await client.get(
                    f"{self.base_url}/services/search/jobs/{sid}/results",
                    auth=self.auth,
                    params={"output_mode": "json", "count": 1000}
                )
                return results.json().get("results", [])
        except Exception as e:
            logger.warning(f"Splunk search unavailable: {e}")
            return []

    async def send_event(self, event: dict, source: str = "ai_ops_intelligence") -> bool:
        if not settings.SPLUNK_HEC_TOKEN:
            logger.warning("HEC token not set — skipping")
            return False
        try:
            headers = {
                "Authorization": f"Splunk {settings.SPLUNK_HEC_TOKEN}",
                "Content-Type":  "application/json"
            }
            payload = {
                "event":  event,
                "source": source,
                "index":  "main"
            }
            logger.info(f"Sending to HEC: {self.hec_url} source={source}")
            async with httpx.AsyncClient(verify=False, timeout=10) as client:
                resp = await client.post(
                    f"{self.hec_url}/services/collector/event",
                    headers=headers,
                    json=payload
                )
                logger.info(f"HEC response: {resp.status_code} — {resp.text}")
                if resp.status_code == 200:
                    logger.info(f"✅ Event sent to Splunk source={source}")
                    return True
                else:
                    logger.warning(f"HEC failed: {resp.status_code} {resp.text}")
                    return False
        except Exception as e:
            logger.warning(f"HEC exception: {e}")
            return False
