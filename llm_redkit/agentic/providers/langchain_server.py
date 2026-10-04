import httpx


class LangChainServerClient:
    """For agents exposed via LangServe or custom FastAPI/Flask endpoints."""

    def __init__(self, url, timeout=120):
        self.url = url.rstrip("/")
        self.timeout = timeout

    def run(self, message):
        with httpx.Client(timeout=self.timeout) as c:
            r = c.post(self.url, json={"input": message})
            r.raise_for_status()
            data = r.json()

        tool_calls = []
        for step in (data.get("intermediate_steps") or []):
            if isinstance(step, (list, tuple)) and len(step) >= 2:
                action = step[0]
                name = getattr(action, "tool", None) or \
                       (action.get("tool") if isinstance(action, dict) else None)
                args = getattr(action, "tool_input", None) or \
                       (action.get("tool_input") if isinstance(action, dict) else None)
                tool_calls.append({"name": name, "args": args})
            elif isinstance(step, dict):
                tool_calls.append({
                    "name": step.get("tool"),
                    "args": step.get("tool_input"),
                })

        return {
            "final": data.get("output") or data.get("response"),
            "tool_calls": tool_calls,
            "status": "completed",
        }
