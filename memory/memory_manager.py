import json
import aiofiles
from datetime import datetime
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger("MemoryManager")

class MemoryManager:
    def __init__(self):
        self.path = settings.MEMORY_FILE

    async def save_incident(self, report: dict):
        incidents = await self._load()
        report["saved_at"] = datetime.utcnow().isoformat()
        incidents.append(report)
        incidents = incidents[-500:]
        await self._write(incidents)
        logger.info(f"Incident saved. Total: {len(incidents)}")

    async def get_recent(self, n: int = 10) -> list:
        incidents = await self._load()
        return incidents[-n:]

    async def search(self, keyword: str) -> list:
        incidents = await self._load()
        return [i for i in incidents if keyword.lower() in json.dumps(i).lower()]

    async def _load(self) -> list:
        try:
            async with aiofiles.open(self.path, "r") as f:
                return json.loads(await f.read())
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    async def _write(self, data: list):
        async with aiofiles.open(self.path, "w") as f:
            await f.write(json.dumps(data, indent=2))
