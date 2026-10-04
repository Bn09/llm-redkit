import asyncio
import os
import httpx


class AsyncLLMClient:
    """Async version of LLMClient. Reuses cache from LLMClient."""

    def __init__(self, base_url, api_key=None, model="gpt-4o-mini",
                 timeout=120.0, headers=None, concurrency=10):
        from .cache import ResponseCache
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("REDKIT_API_KEY", "")
        self.model = model
        self.timeout = timeout
        self.extra_headers = headers or {}
        self.concurrency = concurrency
        self.cache = ResponseCache(
            enabled=(os.environ.get("REDKIT_NO_CACHE") != "1")
        )

    async def _one(self, client, sem, prompt, system):
        async with sem:
            cached = self.cache.get(self.base_url, self.model, prompt, system)
            if cached is not None:
                return cached
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": prompt})
            payload = {"model": self.model, "messages": messages,
                       "temperature": 0.0}
            headers = {"Content-Type": "application/json",
                       "Authorization": "Bearer " + self.api_key,
                       **self.extra_headers}
            r = await client.post(self.base_url + "/chat/completions",
                                  json=payload, headers=headers)
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]
            self.cache.set(self.base_url, self.model, prompt, system, reply)
            return reply

    async def chat_many(self, items, system=None):
        """items: list of prompts. Returns list of replies (order preserved)."""
        sem = asyncio.Semaphore(self.concurrency)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            tasks = [self._one(client, sem, p, system) for p in items]
            return await asyncio.gather(*tasks, return_exceptions=True)
