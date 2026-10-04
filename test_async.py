import asyncio
import time
from llm_redkit.async_client import AsyncLLMClient

async def main():
    c = AsyncLLMClient("http://localhost:11434/v1", "ollama",
                       "llama3.1:8b", concurrency=5)
    prompts = [
        "Say hello in one word.",
        "Say goodbye in one word.",
        "Say yes in one word.",
        "Say no in one word.",
        "Say maybe in one word.",
    ]
    t0 = time.time()
    replies = await c.chat_many(prompts)
    dt = time.time() - t0
    print(f"elapsed: {dt:.1f}s")
    for p, r in zip(prompts, replies):
        print(f"  {p!r} -> {r!r}")

asyncio.run(main())
