# BillGeneratorV01 — Micro-benchmarks

Usage:
```bash
python tools/benchmarks/bench_main.py
```

## Targets

| Function          | Description               | Typical Time (ms) |
| ----------------- | ------------------------- | ----------------- |
| process_batch     | Full I/O + PDF render     | 800–1200          |
| read_excel_cached | Data ingestion w/ caching | 100–200           |

## Notes

* Each run averages multiple trials.
* Use before and after optimization to measure gain.