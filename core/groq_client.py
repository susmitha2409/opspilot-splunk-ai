import asyncio
import itertools
from groq import AsyncGroq
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

class GroqClient:
    def __init__(self, api_key: str = None):
        self.dedicated_key = api_key
        self._keys         = settings.get_groq_keys()
        self._key_cycle    = itertools.cycle(self._keys) if self._keys else None
        self.model         = settings.GROQ_MODEL
        if not self._keys:
            logger.error("No Groq API keys configured!")
        else:
            logger.info(f"GroqClient ready with {len(self._keys)} API key(s)")

    def _get_client(self) -> AsyncGroq:
        if self.dedicated_key:
            return AsyncGroq(api_key=self.dedicated_key)
        if self._key_cycle:
            return AsyncGroq(api_key=next(self._key_cycle))
        raise ValueError("No Groq API keys available")

    async def reason(self, system_prompt: str, user_prompt: str) -> str:
        last_error = None
        for attempt in range(len(self._keys) or 1):
            try:
                client   = self._get_client()
                response = await client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_prompt}
                    ],
                    max_tokens=settings.GROQ_MAX_TOKENS,
                    temperature=0.2
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                err_str    = str(e).lower()
                if "rate_limit" in err_str:
                    logger.warning(f"Rate limit on key {attempt+1}, trying next key...")
                    await asyncio.sleep(1)
                    continue
                else:
                    logger.error(f"Groq error: {e}")
                    return f"ERROR: {str(e)}"
        logger.error(f"All keys exhausted. Last error: {last_error}")
        return f"ERROR: All API keys rate limited. Try again shortly."

    async def stream_reason(self, system_prompt: str, user_prompt: str):
        try:
            client = self._get_client()
            stream = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt}
                ],
                max_tokens=settings.GROQ_MAX_TOKENS,
                stream=True
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"ERROR: {str(e)}"
