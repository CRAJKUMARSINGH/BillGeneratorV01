#!/bin/bash
set -e
echo "Running BillGeneratorV01 profiling..."
python3 tools/profile/profile_app.py --module deployable_app --func process_batch --args "['INPUT_FILES/3rdFinalNoExtra.xlsx']" --pyinstrument || true
echo "Done. Reports in tools/profile/"