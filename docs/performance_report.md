# Performance Report — ia_service_core (stress)

## Summary
- Date: 21 March 2026
- Target: `ia_service_core` (RAG + CAG)
- Test: stress run with mocks to avoid GPU/VRAM usage

## Environment
- Host OS: Linux (developer workstation)
- Python venv: `.venv` in repo root
- Key libs: `diskcache`, `numpy`, `fastapi`, `uvicorn`

## Test configuration
- Script: `ia_service_core/tests/profiling/profile_cag.py`
- Warmup: 30 calls
- Workload: 2000 requests, concurrency 50 (mocked LLM & vector repo)

## Results (aggregated)
- Requests: 2000
- Concurrency: 50
- Total elapsed (s): 4.772
- Median latency (P50): 99.08 ms
- Peak RSS: 54,216 KB (~53 MB)

## Top traced allocations (tracemalloc snapshot)
- profile file allocations (test harness) and `diskcache` entries dominate snapshot output.

## Observations
- Under stress load the service remained stable and memory usage stayed well under the 16GB constraint (peak ~53MB in this mocked run).
- Median latency ~100ms with concurrency 50 using mocked LLM/DB indicates the service orchestration overhead and cache mechanics are reasonable.
- Disk spill behaviour observed via `DiskCacheAdapter` tests — cache entries persisted to disk and in-memory index kept bounded.

## Actions performed (implementation highlights)
- Introduced `CacheRepository` port and `DiskCacheAdapter` (disk-backed LRU + async wrappers).
- Converted PDF parsing to non-blocking via a bounded `ThreadPoolExecutor` and `PARSER_MAX_WORKERS` setting.
- Added an `asyncio.Semaphore` protecting the ingest endpoint; route returns HTTP 429 when saturated.
- Added structured JSON logging and request_id propagation middleware.
- Implemented background invalidation after ingests to avoid blocking requests.

## Recommended next steps
1. Add CI job to run the profiling harness on PRs that touch CAG/RAG code (smoke run as gate).
2. Add `trivy` image scan in CI and an artifact upload step for raw profiling output.
3. Incrementally fix linter warnings (flake8) in modified files before merging to protected branch.

## Artifacts
- Raw output: `ia_service_core/tests/profiling/profile_cag.py` run captured in terminal (available on developer machine).
- Tests: `tests/test_cag.py` (validates spill-to-disk) and `tests/test_ingest_async.py` (validates non-blocking parser).

## Notes and caveats
- This run used mocked embeddings and vector repo to avoid GPU/VRAM dependencies and to measure pure service orchestration + cache behaviour. Production behaviour will vary with the real LLM and Qdrant IO characteristics.
