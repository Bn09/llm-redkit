import time
import httpx


class OpenAIAssistantsClient:
    """Real agent client for OpenAI Assistants API v2."""

    def __init__(self, api_key, assistant_id,
                 base_url="https://api.openai.com/v1",
                 timeout=120):
        self.api_key = api_key
        self.assistant_id = assistant_id
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.headers = {
            "Authorization": "Bearer " + api_key,
            "OpenAI-Beta": "assistants=v2",
            "Content-Type": "application/json",
        }

    def run(self, message):
        with httpx.Client(timeout=self.timeout) as c:
            t = c.post(self.base_url + "/threads",
                       headers=self.headers, json={}).json()
            thread_id = t["id"]

            c.post(self.base_url + "/threads/" + thread_id + "/messages",
                   headers=self.headers,
                   json={"role": "user", "content": message})

            r = c.post(self.base_url + "/threads/" + thread_id + "/runs",
                       headers=self.headers,
                       json={"assistant_id": self.assistant_id}).json()
            run_id = r["id"]

            status = "queued"
            for _ in range(80):
                st = c.get(
                    self.base_url + "/threads/" + thread_id + "/runs/" + run_id,
                    headers=self.headers).json()
                status = st["status"]
                if status in ("completed", "failed", "cancelled", "expired"):
                    break
                time.sleep(1.5)

            msgs = c.get(
                self.base_url + "/threads/" + thread_id + "/messages",
                headers=self.headers).json()
            data = msgs.get("data", [])
            if not data:
                return {"final": None, "tool_calls": [], "status": status}

            first = data[0]
            content = first.get("content", []) or []
            text = "".join(
                b.get("text", {}).get("value", "")
                for b in content if b.get("type") == "text"
            )
            tools = []
            for b in content:
                if b.get("type") == "tool_calls":
                    for tc in b.get("tool_calls", []):
                        fn = tc.get("function", {})
                        tools.append({
                            "name": fn.get("name"),
                            "args": fn.get("arguments"),
                        })
            return {"final": text, "tool_calls": tools, "status": status}
