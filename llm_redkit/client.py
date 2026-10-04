from .cache import ResponseCacheself.cache = ResponseCache(enabled=(os.environ.get("REDKIT_NO_CACHE") != "1"))
self.last_cached = Falsecached = self.cache.get(self.base_url, self.model, prompt, system)
if cached is not None:
    self.last_cached = True
    return cached
self.last_cached = Falseself.cache.set(self.base_url, self.model, prompt, system, reply)
return replyimport httpx, os
from typing import Optional

class LLMClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None,
                 model: str = "gpt-4o-mini", timeout: float = 60.0,
                 headers: Optional[dict] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("REDKIT_API_KEY", "")
        self.model = model
        self.timeout = timeout
        self.extra_headers = headers or {}

    def chat(self, prompt: str, system: Optional[str] = None,
             temperature: float = 0.0) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": self.model, "messages": messages,
                   "temperature": temperature}
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {self.api_key}",
                   **self.extra_headers}
        with httpx.Client(timeout=self.timeout) as c:
            r = c.post(f"{self.base_url}/chat/completions",
                       json=payload, headers=headers)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

    def chat_raw(self, messages: list, tools: list | None = None) -> dict:
        payload = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        headers = {"Content-Type": "application/json",
                   "Authorization": f"Bearer {self.api_key}",
                   **self.extra_headers}
        with httpx.Client(timeout=self.timeout) as c:
            r = c.post(f"{self.base_url}/chat/completions",
                       json=payload, headers=headers)
            r.raise_for_status()
            return r.json()

    def chat_raw(self, messages, tools=None):
        payload = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
            **self.extra_headers,
        }
        with httpx.Client(timeout=self.timeout) as c:
            r = c.post(self.base_url + "/chat/completions",
                       json=payload, headers=headers)
            r.raise_for_status()
            return r.json()
