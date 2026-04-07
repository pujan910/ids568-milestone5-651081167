import asyncio
import time
import psutil
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
from src.config import settings
from src.caching import cache
from src.batching import batcher

# Stats tracking
stats = {"requests": 0, "cache_hits": 0, "cache_misses": 0, "start_time": time.time()}

def run_model(prompts: list, max_tokens: int) -> list:
    results = []
    for prompt in prompts:
        out = generator(prompt, max_new_tokens=max_tokens, do_sample=False)
        results.append(out[0]["generated_text"])
    return results

@asynccontextmanager
async def lifespan(app: FastAPI):
    global generator
    print(f"Loading model: {settings.model_name}")
    generator = pipeline("text-generation", model=settings.model_name)
    print("Model loaded!")
    await batcher.start(run_model)
    yield

app = FastAPI(title="LLM Inference Server", lifespan=lifespan)

class InferenceRequest(BaseModel):
    prompt: str
    max_tokens: int = 100

class InferenceResponse(BaseModel):
    text: str
    cached: bool
    latency_ms: float

@app.post("/generate", response_model=InferenceResponse)
async def generate(request: InferenceRequest):
    start = time.time()
    stats["requests"] += 1

    # Check cache first
    cached_result = await cache.get(request.prompt, settings.model_name, request.max_tokens)
    if cached_result:
        stats["cache_hits"] += 1
        return InferenceResponse(text=cached_result, cached=True, latency_ms=(time.time()-start)*1000)

    stats["cache_misses"] += 1
    result = await batcher.submit(request.prompt, request.max_tokens)
    await cache.set(request.prompt, settings.model_name, request.max_tokens, result)
    return InferenceResponse(text=result, cached=False, latency_ms=(time.time()-start)*1000)

@app.get("/health")
async def health():
    return {"status": "ok", "model": settings.model_name}

@app.get("/stats")
async def get_stats():
    cache_stats = await cache.stats()
    uptime = time.time() - stats["start_time"]
    hit_rate = stats["cache_hits"] / max(stats["requests"], 1)
    return {
        "uptime_seconds": uptime,
        "total_requests": stats["requests"],
        "cache_hits": stats["cache_hits"],
        "cache_misses": stats["cache_misses"],
        "cache_hit_rate": hit_rate,
        "cache": cache_stats,
        "batching": {
            "total_batches": batcher.total_batches,
            "total_requests": batcher.total_requests,
        },
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
        }
    }
