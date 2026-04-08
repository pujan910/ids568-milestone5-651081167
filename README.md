# IDS568 Milestone 5 — LLM Inference Optimization

## Overview

This project implements an optimized LLM inference server with:

- Dynamic request batching
- In-memory caching with TTL and eviction
- Performance benchmarking
- Governance and risk analysis
- Performance visualization

The goal is to improve latency, throughput, and resource utilization for LLM inference workloads.

---

## Setup

### 0. Clone Repository

```bash
git clone https://github.com/pujan910/ids568-milestone5-651081167.git
cd ids568-milestone5-651081167
```

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the server

```bash
python -m uvicorn src.server:app --host 0.0.0.0 --port 8000
```

### 3. Test it works

```bash
curl http://localhost:8000/health
```

Expected output:

```json
{"status":"ok","model":"facebook/opt-125m"}
```

### 4. Run benchmarks (open a new terminal tab first)

```bash
python benchmarks/run_benchmarks.py
python benchmarks/load_generator.py
```

---

## Generate Visualizations

```bash
python analysis/visualizations/generate_charts.py
```

Generated charts:

- cold_vs_warm.png
- batching_latency.png
- hit_rate_over_time.png
- load_comparison.png

Saved in:

```
analysis/visualizations/
```

---

## Configuration

Edit `.env` file to change settings:

- MAX_BATCH_SIZE - max requests per batch (default: 8)
- BATCH_TIMEOUT_MS - max wait time in ms (default: 50)
- CACHE_TTL_SECONDS - cache expiry time (default: 300)
- CACHE_MAX_ENTRIES - max cached items (default: 1000)

If `.env` is not provided, defaults from `src/config.py` are used.

---

## API Endpoints

### Health Check

GET /health

Returns server and model status.

---

### Generate Text

POST /generate

Example:

```bash
curl -X POST http://localhost:8000/generate \
-H "Content-Type: application/json" \
-d '{"prompt":"Explain machine learning","max_tokens":50}'
```

---

### Metrics

GET /stats

Returns:

- Cache hit rate
- Batch size metrics
- CPU usage
- Memory usage
- Request counts

---

## Benchmark Outputs

Benchmark results saved to:

```
benchmarks/results/
```

Includes:

- cold_vs_warm.json
- batching.json
- hit_rate.json
- low_load.json
- medium_load.json
- high_load.json

---

## Project Structure

```
src/
 ├── server.py
 ├── batching.py
 ├── caching.py
 └── config.py

benchmarks/
 ├── run_benchmarks.py
 ├── load_generator.py
 └── results/

analysis/
 ├── performance_report.pdf
 ├── governance_memo.pdf
 └── visualizations/
```

---

## Optimization Features

### Dynamic Batching

- Hybrid timeout + size batching
- Async queue processing
- Executor-based model execution

Improves throughput under load.

---

### Caching

- SHA-256 hashed keys
- TTL expiration
- Max-entry eviction
- Thread-safe access

Improves latency for repeated requests.

---

## Performance Improvements

Observed improvements:

- Cold request: ~700ms
- Warm cache: ~1ms
- Cache hit rate: ~70%
- Increased throughput under concurrent load

---

## Governance Considerations

- Prompt privacy protection
- Hash-based cache keys
- TTL-based retention
- Risk mitigation strategies

See:

```
analysis/governance_memo.pdf
```

---

## Performance Analysis

Detailed benchmarking and analysis available in:

```
analysis/performance_report.pdf
```

---

## Requirements

- Python 3.9+
- FastAPI
- Transformers
- PyTorch
- Uvicorn
- Matplotlib

Install using:

```bash
pip install -r requirements.txt
```

---

## Submission

Repository includes:

- Dynamic batching implementation
- Cache optimization
- Benchmarking scripts
- Performance analysis
- Governance memo
- Visualization charts

---
