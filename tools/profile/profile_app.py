#!/usr/bin/env python3
"""
Profile the BillGenerator backend pipeline (non-computation only).

Usage example:
  python tools/profile/profile_app.py --module batch_processor --func process_batch --args "['INPUT_FILES', 'OUTPUT_FILES']" --pyinstrument
"""

import argparse, cProfile, pstats, importlib, json
from pathlib import Path
import sys
import os

# Add the current directory to sys.path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

PROFILE_DIR = Path(__file__).parent
PROFILE_STATS = PROFILE_DIR / "profile.stats"
PROFILE_SUMMARY = PROFILE_DIR / "profile_summary.txt"
PYINSTRUMENT_HTML = PROFILE_DIR / "pyinstrument_report.html"

def run_cprofile(module, func, args):
    print(f"Importing module: {module}")
    m = importlib.import_module(module)
    print(f"Getting function: {func}")
    f = getattr(m, func)
    print(f"Creating profiler")
    profiler = cProfile.Profile()
    profiler.enable()
    print(f"Running function with args: {args}")
    f(*args)
    profiler.disable()
    print(f"Saving profile stats to: {PROFILE_STATS}")
    profiler.dump_stats(str(PROFILE_STATS))
    print(f"Saving profile summary to: {PROFILE_SUMMARY}")
    with open(PROFILE_SUMMARY, "w") as fh:
        ps = pstats.Stats(profiler, stream=fh).sort_stats("cumtime")
        ps.print_stats(80)
    print(f"[✓] cProfile written → {PROFILE_SUMMARY}")

def run_pyinstrument(module, func, args):
    try:
        from pyinstrument import Profiler
    except ImportError:
        print("pyinstrument not installed; skipping HTML profile.")
        return
    print(f"Running pyinstrument on {module}.{func}")
    m = importlib.import_module(module)
    f = getattr(m, func)
    profiler = Profiler()
    profiler.start()
    f(*args)
    profiler.stop()
    PYINSTRUMENT_HTML.write_text(profiler.output_html())
    print(f"[✓] pyinstrument HTML → {PYINSTRUMENT_HTML}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--module", default="batch_processor")
    ap.add_argument("--func", default="process_batch")
    ap.add_argument("--args", default="[]")
    ap.add_argument("--pyinstrument", action="store_true")
    a = ap.parse_args()
    print(f"Parsing args: {a.args}")
    args = json.loads(a.args) if a.args else []
    print(f"Running cProfile on {a.module}.{a.func} with args {args}")
    run_cprofile(a.module, a.func, args)
    if a.pyinstrument:
        print("Running pyinstrument")
        run_pyinstrument(a.module, a.func, args)

if __name__ == "__main__":
    main()