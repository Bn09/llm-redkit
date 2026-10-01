import json
from ..client import LLMClient
from .spec import AgentSpec

class AgentRunner:
    def __init__(self, client, spec):
        self.client = client
        self.spec = spec
        self.trace = []

    def _tools_schema(self):
        return [{
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            }
        } for t in self.spec.tools]

    def _simulate_tool(self, name, args):
        return {"ok": True, "sandbox": True,
                "echo": {"tool": name, "args": args}}

    def run(self, user_message):
        self.trace = []
        messages = [
            {"role": "system", "content": self.spec.system_prompt},
            {"role": "user", "content": user_message},
        ]
        for _ in range(self.spec.max_turns):
            try:
                raw = self.client.chat_raw(messages, tools=self._tools_schema())
            except Exception as e:
                return {"final": None, "trace": self.trace,
                        "tools_called": self._collect_tools(),
                        "error": str(e)}
            msg = raw["choices"][0]["message"]
            self.trace.append(msg)
            tool_calls = msg.get("tool_calls") or []
            if not tool_calls:
                return {"final": msg.get("content", ""),
                        "trace": self.trace,
                        "tools_called": self._collect_tools()}
            messages.append(msg)
            for tc in tool_calls:
                fn = tc["function"]["name"]
                try:
                    args = json.loads(tc["function"]["arguments"])
                except Exception:
                    args = {}
                result = self._simulate_tool(fn, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": json.dumps(result),
                })
        return {"final": None, "trace": self.trace,
                "tools_called": self._collect_tools(),
                "error": "max_turns"}

    def _collect_tools(self):
        out = []
        for m in self.trace:
            for tc in m.get("tool_calls") or []:
                out.append({
                    "name": tc["function"]["name"],
                    "args": tc["function"]["arguments"],
                })
        return out
