## Goal
Produce a performance report identifying non-computation bottlenecks (I/O, template rendering, PDF conversion, Streamlit).

## Tasks
- Run cProfile and pyinstrument on pipeline entry.
- Produce profile_summary.txt, pyinstrument HTML (optional).
- Fill PERFORMANCE_REPORT_TEMPLATE.md and attach graphs.

## Acceptance Criteria
- profile_summary.txt and profile_callgraph.png added to `tools/profile/`.
- PERFORMANCE_REPORT_TEMPLATE.md filled with observations and recommended fixes.