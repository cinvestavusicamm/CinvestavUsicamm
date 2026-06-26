# PR Skeleton — Summary for reviewers

## Title
- feat(rag/cag): decouple parser, add async parser, disk-backed semantic cache, observability

## Description
- What changed: Introduced `CacheRepository` port and `DiskCacheAdapter`; converted `PDFParser` to non-blocking with a bounded threadpool; added ingest concurrency protection; added structured logging and request_id middleware; added profiling harness and tests.
- Why: Reduce coupling, prevent event-loop blocking on PDF parsing, provide a memory-bounded semantic cache with spill-to-disk, and improve observability and profiling for performance validation.

## Related Issues
- N/A

## How To Test
- From repo root create and activate `.venv`, install requirements, then run unit/smoke tests listed in `ia_service_core/tests`.
- Run profiling harness:
```bash
cd ia_service_core
.venv/bin/python -c "import sys,runpy,asyncio; m=runpy.run_path('tests/profiling/profile_cag.py'); main=m.get('main'); asyncio.run(main(total=2000, concurrency=50))"
```

## Checklist
- [ ] Tests pass locally
- [ ] Linter warnings reviewed
- [ ] Performance report attached (`docs/performance_report.md`)

## Files changed (high level)
- `src/application/ports/input.py` — added async DocumentParser port
- `src/application/use_cases/ingest_doc.py` — DI for parser, background invalidation
- `src/application/use_cases/chat_rag.py` — cache integration
- `src/infrastructure/utils/pdf_parser.py` — async wrapper using ThreadPoolExecutor
- `src/infrastructure/cache/diskcache_adapter.py` — new adapter
- `src/infrastructure/api/dependencies.py` — wire cache, parser, semaphore
- `tests/profiling/profile_cag.py`, `tests/test_cag.py`, `tests/test_ingest_async.py` — new tests

## MoProSoft (minimal) checklist
- [ ] Artefactos de diseño y reportes (docs/performance_report.md)
- [ ] Evidencia de pruebas de estrés y smoke
- [ ] Identificación de riesgos y mitigaciones
