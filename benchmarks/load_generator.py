import asyncio
import aiohttp
import time
import random

PROMPTS = [
    "Explain machine learning in simple terms",
    "What is the capital of France?",
    "Write a haiku about computers",
    "What is 2 + 2?",
    "Describe the water cycle",
    "What is machine learning?",
    "Explain machine learning in simple terms",
    "What is the capital of France?",
    "Tell me about neural networks",
    "What is deep learning?",
]

async def send_request(session, prompt, results):
    start = time.time()
    try:
        async with session.post(
            "http://localhost:8000/generate",
            json={"prompt": prompt, "max_tokens": 50},
            timeout=aiohttp.ClientTimeout(total=60)
        ) as resp:
            data = await resp.json()
            latency = (time.time() - start) * 1000
            results.append({
                "prompt": prompt[:30],
                "latency_ms": latency,
                "cached": data.get("cached", False),
                "success": True
            })
    except Exception as e:
        results.append({"prompt": prompt[:30], "latency_ms": -1, "cached": False, "success": False, "error": str(e)})

async def run_load(concurrency: int, num_requests: int):
    results = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(num_requests):
            prompt = PROMPTS[i % len(PROMPTS)]
            tasks.append(send_request(session, prompt, results))
            if len(tasks) >= concurrency:
                await asyncio.gather(*tasks)
                tasks = []
        if tasks:
            await asyncio.gather(*tasks)
    return results

if __name__ == "__main__":
    import json, os
    os.makedirs("benchmarks/results", exist_ok=True)
    for level, (conc, reqs) in [("low", (5, 20)), ("medium", (20, 60)), ("high", (50, 100))]:
        print(f"Running {level} load: {conc} concurrent, {reqs} requests...")
        results = asyncio.run(run_load(conc, reqs))
        with open(f"benchmarks/results/{level}_load.json", "w") as f:
            json.dump(results, f, indent=2)
        success = [r for r in results if r["success"]]
        hits = [r for r in success if r["cached"]]
        avg_lat = sum(r["latency_ms"] for r in success) / max(len(success), 1)
        print(f"  Done. Success: {len(success)}/{len(results)}, Cache hits: {len(hits)}, Avg latency: {avg_lat:.1f}ms")
