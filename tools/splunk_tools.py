from core.splunk_client import SplunkClient
from config.logging_config import get_logger

logger = get_logger("SplunkTools")

class SplunkTools:
    def __init__(self):
        self.client = SplunkClient()

    async def search(self, query: str, earliest: str = "-1h", latest: str = "now") -> list:
        logger.info(f"Searching Splunk: {query}")
        return await self.client.run_search(query, earliest, latest)

    async def get_errors(self, service: str = "*", minutes: int = 30) -> list:
        query = f'index=main level=ERROR service="{service}" earliest=-{minutes}m'
        return await self.client.run_search(query)
