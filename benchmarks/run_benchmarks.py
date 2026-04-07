import asyncio
import aiohttp
import time
import json
import os
import argparse

os.makedirs("benchmarks/results", exist_ok=True)
BASE_URL = "http://localhost:8000"

PROMPTS_UNIQUE = [f"Tell me about topic number {i}" for i in range(50)]
PROMPTS_REPEATED = ["Explain machine learning in simple terms"] * 20

async def single_request(session, prompt, max_tokens=50):
    start = time.time()
    async with session.post(f"{BASE_URL}/generate",
        json={"prompt": prompt, "max_tokens": max_tokens},
        timeout=aiohttp.ClientTimeout(total=120)) as r:
        data = await r.json()
        return {"latency_ms": (time.time()-start)*1000, "cached": data.get("cached", False), "text": data.get("text","")}

async def benchmark_cold_vs_warm(session):
    print("\n--- Cold vs Warm Cache ---")
    prompt = "What is the meaning of life according to philosophy?"
    cold = await single_request(session, prompt)
    print(f"  Cold: {cold['latency_ms']:.1f}ms, cached={cold['cached']}")
    warm = await single_request(session, prompt)
    print(f"  Warm: {warm['latency_ms']:.1f}ms, cached={warm['cached']}")
    result = {"cold_ms": cold["latency_ms"], "warm_ms": warm["latency_ms"], "speedup": cold["latency_ms"]/max(warm["latency_ms"],1)}
    with open("benchmarks/results/cold_vs_warm.json","w") as f:
        json.dump(result, f, indent=2)
    return result

async def benchmark_batching(session):
    print("\n--- Batching Benchmark ---")
    results = []
    tasks = [single_request(session, p) for p in PROMPTS_UNIQUE[:10]]
    start = time.time()
    responses = await asyncio.gather(*tasks)
    total = time.time() - start
    for r in responses:
        results.append(r["latency_ms"])
    avg = sum(results)/len(results)
    print(f"  10 concurrent requests: avg={avg:.1f}ms, total_wall={total*1000:.1f}ms")
    out = {"avg_latency_ms": avg, "total_wall_ms": total*1000, "individual": results}
    with open("benchmarks/results/batching.json","w") as f:
        json.dump(out, f, indent=2)
    return out

async def benchmark_hit_rate(session):
    print("\n--- Cache Hit Rate Over Time ---")
    results = []
    prompts = PROMPTS_REPEATED + PROMPTS_UNIQUE[:20]
    for i, prompt in enumerate(prompts):
        r = await single_request(session, prompt)
        results.append({"request_num": i+1, "cached": r["cached"], "latency_ms": r["latency_ms"]})
    hits = sum(1 for r in results if r["cached"])
    print(f"  Hit rate: {hits}/{len(results)} = {hits/len(results)*100:.1f}%")
    with open("benchmarks/results/hit_rate.json","w") as f:
        json.dump(results, f, indent=2)
    return results

async def main():
    parser = argparse.ArgumentParser(description="Run LLM inference benchmarks")
    parser.add_argument("--help-info", action="store_true", help="Show benchmark info")
    args = parser.parse_args()
    print("Starting benchmarks against", BASE_URL)
    async with aiohttp.ClientSession() as session:
        # Warmup
        print("Warming up model...")
        await single_request(session, "hello", 10)
        await benchmark_cold_vs_warm(session)
        await benchmark_batching(session)
        await benchmark_hit_rate(session)
    print("\nAll benchmarks complete! Results saved to benchmarks/results/")

if __name__ == "__main__":
    asyncio.run(main())
