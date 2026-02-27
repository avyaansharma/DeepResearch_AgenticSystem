import asyncio
import random
from itertools import cycle
from ..config import OPENAI_API_KEYS, GEMINI_API_KEYS, REQUEST_DELAY


class LLMManager:
    def __init__(self):
        self.openai_keys = cycle(OPENAI_API_KEYS) if OPENAI_API_KEYS else None
        self.gemini_keys = cycle(GEMINI_API_KEYS) if GEMINI_API_KEYS else None
        self._lock = asyncio.Lock()

    def get_openai_key(self):
        if not self.openai_keys:
            return None
        return next(self.openai_keys)

    def get_gemini_key(self):
        if not self.gemini_keys:
            return None
        return next(self.gemini_keys)

    async def throttle(self):
        """Simple throttling to avoid rate limits."""
        await asyncio.sleep(REQUEST_DELAY + random.uniform(0, 1))

llm_manager = LLMManager()
