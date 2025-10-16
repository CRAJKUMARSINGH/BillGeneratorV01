This PR adds:
- A GitHub Actions CI workflow (.github/workflows/ci.yml) to run tests and lint on PRs.
- Profiling tooling (tools/profile/*) with `profile_app.py` and run script.
- PERFORMANCE_REPORT_TEMPLATE.md for standardized performance reporting.

No computation logic changed. These are developer tools and CI configuration to support the performance optimization plan outlined in the project roadmap.

Next steps (once merged):
- Run the profiling script on representative sample files; attach profile outputs to W1 issue.
- Iterate on low-risk performance fixes in W2.