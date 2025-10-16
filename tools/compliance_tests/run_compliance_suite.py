"""
Compliance validation suite.
Executes all statutory format validators across sample outputs.
"""

from tools.validators.validate_output import validate_csv, validate_xml, validate_pdf_basic
from pathlib import Path
import json

def run_suite():
    results = {}
    outdir = Path("output")
    csvs = list(outdir.glob("*.csv"))
    xmls = list(outdir.glob("*.xml"))
    pdfs = list(outdir.glob("*.pdf"))

    for f in csvs:
        ok, msg = validate_csv(f, ["BillID","Date","Amount"])
        results[str(f)] = {"ok": ok, "msg": msg}
    for f in xmls:
        ok, msg = validate_xml(f, "templates/statutory/sample_schema.xsd")
        results[str(f)] = {"ok": ok, "msg": msg}
    for f in pdfs:
        ok, msg = validate_pdf_basic(f)
        results[str(f)] = {"ok": ok, "msg": msg}

    Path("validation_report").mkdir(exist_ok=True)
    with open("validation_report/report.json", "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    print("Compliance report written to validation_report/report.json")
    failed = [k for k,v in results.items() if not v["ok"]]
    if failed:
        print("❌ Non-compliant files:", failed)
        return 2
    print("✅ All files compliant.")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(run_suite())