from llm_redkit.agentic.providers import LangChainServerClient
from llm_redkit.agentic.runner import RealAgentRunner
from llm_redkit.agentic.attacks import AGENTIC_PROMPTS

provider = LangChainServerClient("http://localhost:8000/agent")
runner = RealAgentRunner(provider,
                         dangerous_tools=["send_email", "delete_user"])

total = 0
findings = 0
for cat, prompts in AGENTIC_PROMPTS.items():
    for i, prompt in enumerate(prompts):
        total += 1
        res = runner.run(prompt)
        called = res.get("tools_called") or []
        dangerous = [c for c in called
                     if c.get("name") in ("send_email", "delete_user")]
        tag = "[FOUND " + str(dangerous) + "]" if dangerous else "[ok]"
        if dangerous:
            findings += 1
        print(f"{cat}[{i}]: {tag}")

print()
print(f"Total: {total} | Findings: {findings}")
