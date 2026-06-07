from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    SPLUNK_HOST: str = "localhost"
    SPLUNK_PORT: int = 8089
    SPLUNK_USERNAME: str = "admin"
    SPLUNK_PASSWORD: str = "changeme"
    SPLUNK_INDEX: str = "main"
    SPLUNK_HEC_TOKEN: str = ""
    SPLUNK_HEC_PORT: int = 8088

    # 5 Groq API Keys
    GROQ_API_KEY_1: str = ""
    GROQ_API_KEY_2: str = ""
    GROQ_API_KEY_3: str = ""
    GROQ_API_KEY_4: str = ""
    GROQ_API_KEY_5: str = ""

    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MAX_TOKENS: int = 4096

    MCP_HOST: str = "localhost"
    MCP_PORT: int = 9000

    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    MEMORY_FILE: str = "memory/incident_memory.json"

    def get_groq_keys(self) -> list:
        """Return all configured keys as a list."""
        keys = [
            self.GROQ_API_KEY_1,
            self.GROQ_API_KEY_2,
            self.GROQ_API_KEY_3,
            self.GROQ_API_KEY_4,
            self.GROQ_API_KEY_5,
        ]
        # Only return non-empty keys
        return [k for k in keys if k.strip()]

    class Config:
        env_file = ".env"

settings = Settings()
