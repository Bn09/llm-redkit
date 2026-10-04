"""Standalone concurrent scanner. Faster than redkit CLI for large scans."""
import asyncio
import sys
from llm_redkit.async_client import AsyncLLMClient
from llm_redkit.scorer import score
from llm_redkit.attacks import ALL_ATTACKS
from llm_redkit.compliance import map_frameworks


async def scan(base_url, api_key, model, system, concurrency=10):
    client = AsyncLLMClient(base_url, api_key, model,
                            concurrency=concurrency)
    items = []
    meta = []
    for cat, prompts in ALL_ATTACKS.items():
        for i, p in enumerate(prompts):
            items.append(p)
            meta.append((cat, i))
    replies = await client.chat_many(items, system=system)
    verdicts = []
    for (cat, i), reply in zip(meta, replies):
        name = f"{cat}[{i}]"
        if isinstance(reply, Exception):
            verdicts.append({"attack": name, "success": False,
                             "severity": "error", "error": str(reply)})
            continue
        v = score(name, reply, cat)
        verdicts.append({**vars(v), "frameworks": map_frameworks(cat)})
    return verdicts


if __name__ == "__main__":
    import time, json
    base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:11434/v1"
    model = sys.argv[2] if len(sys.argv) > 2 else "llama3.1:8b"
    conc = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    t0 = time.time()
    v = asyncio.run(scan(base, "ollama", model, None, conc))
    dt = time.time() - t0
    findings = sum(1 for x in v if x.get("success"))
    print(f"elapsed: {dt:.1f}s | total: {len(v)} | findings: {findings}")
    with open("concurrent_findings.json", "w") as f:
        json.dump(v, f, indent=2, default=str)
