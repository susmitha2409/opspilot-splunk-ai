from abc import ABC, abstractmethod
from core.groq_client import GroqClient
from core.splunk_client import SplunkClient
from memory.memory_manager import MemoryManager
from config.settings import settings
from config.logging_config import get_logger

# Map each agent index to a specific Groq key
AGENT_KEY_MAP = {
    0: settings.GROQ_API_KEY_1,  # QueryAgent       → Key 1
    1: settings.GROQ_API_KEY_2,  # RCAAgent          → Key 2
    2: settings.GROQ_API_KEY_3,  # RiskAgent         → Key 3
    3: settings.GROQ_API_KEY_4,  # CorrelationAgent  → Key 4
    4: settings.GROQ_API_KEY_5,  # RemediationAgent  → Key 5
}

class BaseAgent(ABC):
    # Override agent_index in each subclass
    agent_index: int = 0

    def __init__(self):
        # Use dedicated key for this agent, fallback to rotation
        dedicated = AGENT_KEY_MAP.get(self.agent_index, "")
        self.groq    = GroqClient(api_key=dedicated if dedicated else None)
        self.splunk  = SplunkClient()
        self.memory  = MemoryManager()
        self.logger  = get_logger(self.__class__.__name__)

    @abstractmethod
    async def run(self, context: dict) -> dict:
        pass

    def build_context_prompt(self, context: dict) -> str:
        return "\n".join([f"{k}: {v}" for k, v in context.items()])
