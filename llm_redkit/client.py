import os
from typing import Optional
import httpx
from .cache import ResponseCache


class LLMClient:
    def __init__(self, base_url, api_key=None, model="gpt-4o-mini",
                 timeout=60.0, headers=None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or os.environ.get("REDKIT_API_KEY", "")
        self.model = model
        self.timeout = timeout
        self.extra_headers = headers or {}
        self.cache = ResponseCache(
            enabled=(os.environ.get("REDKIT_NO_CACHE") != "1")
        )
        self.last_cached = False

    def chat(self, prompt, system=None, temperature=0.0):
        cached = self.cache.get(self.base_url, self.model, prompt, system)
        if cached is not None:
            self.last_cached = True
            return cached
        self.last_cached = False

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {"model": self.model, "messages": messages,
                   "temperature": temperature}
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer " + self.api_key,
                   **self.extra_headers}

        with httpx.Client(timeout=self.timeout) as c:
            r = c.post(self.base_url + "/chat/completions",
                       json=payload, headers=headers)
            r.raise_for_status()
            reply = r.json()["choices"][0]["message"]["content"]

        self.cache.set(self.base_url, self.model, prompt, system, reply)
        return reply

    def chat_raw(self, messages, tools=None):
        payload = {"model": self.model, "messages": messages}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        headers = {"Content-Type": "application/json",
                   "Authorization": "Bearer " + self.api_key,
                   **self.extra_headers}
        with httpx.Client(timeout=self.timeout) as c:
            r = c.post(self.base_url + "/chat/completions",
                       json=payload, headers=headers)
            r.raise_for_status()
            return r.json()
