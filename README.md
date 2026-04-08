# IDS568 Milestone 5 - LLM Inference Optimization

## Setup

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

### 4. Run benchmarks (open a new terminal tab first)
```bash
python benchmarks/run_benchmarks.py
python benchmarks/load_generator.py
```

## Configuration
Edit `.env` file to change settings:
- `MAX_BATCH_SIZE` - max requests per batch (default: 8)
- `BATCH_TIMEOUT_MS` - max wait time in ms (default: 50)
- `CACHE_TTL_SECONDS` - cache expiry time (default: 300)
- `CACHE_MAX_ENTRIES` - max cached items (default: 1000)

## Project Structure
- `src/server.py` - Main FastAPI inference server
- `src/batching.py` - Dynamic request batching logic
- `src/caching.py` - In-memory cache with TTL
- `src/config.py` - Configuration management
- `benchmarks/` - Performance measurement scripts
- `analysis/` - Reports and visualizations
