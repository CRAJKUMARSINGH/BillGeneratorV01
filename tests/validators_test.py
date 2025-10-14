# tests/validators_test.py
from tools.validators.validate_output import validate_csv, validate_xml
from pathlib import Path
import tempfile, csv

def test_validate_csv_ok(tmp_path):
    p = tmp_path / "test.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["BillID","Date","Amount"])
        writer.writerow(["B1","2025-01-01","100.00"])
    ok, msg = validate_csv(str(p), ["BillID","Date","Amount"])
    assert ok, msg

def test_validate_csv_missing(tmp_path):
    p = tmp_path / "test.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["BillID","Amount"])
    ok, msg = validate_csv(str(p), ["BillID","Date","Amount"])
    assert not ok

def test_validate_xml_no_xsd(tmp_path):
    p = tmp_path / "b.xml"
    p.write_text("<Bills></Bills>")
    ok, msg = validate_xml(str(p), None)
    assert ok