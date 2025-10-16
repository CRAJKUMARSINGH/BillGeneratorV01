@echo off
echo Running BillGeneratorV01 profiling...
python tools/profile/profile_app.py --module deployable_app --func process_batch --args "[\"INPUT_FILES/3rdFinalNoExtra.xlsx\"]" --pyinstrument
echo Done. Reports in tools/profile/
pause