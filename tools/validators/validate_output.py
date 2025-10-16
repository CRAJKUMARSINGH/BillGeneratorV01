"""
Validate generated outputs (CSV, XML, PDF) against statutory shape.

- CSV: checks header columns present
- XML: validates against a provided XSD (if provided)
- PDF: checks page count and whether logo appears (heuristic using text extraction)
"""

from pathlib import Path
import csv
import sys

def validate_csv(file_path, required_headers):
    p = Path(file_path)
    if not p.exists():
        return False, f"CSV not found: {file_path}"
    with p.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        try:
            headers = next(reader)
        except StopIteration:
            return False, "CSV empty"
    missing = [h for h in required_headers if h not in headers]
    if missing:
        return False, f"Missing headers: {missing}"
    return True, "CSV headers OK"

def validate_xml(file_path, xsd_path=None):
    p = Path(file_path)
    if not p.exists():
        return False, f"XML not found: {file_path}"
    if xsd_path:
        try:
            import lxml.etree as etree
        except Exception as e:
            return False, f"lxml not installed: {e}"
        try:
            xml_doc = etree.parse(str(p))
            xmlschema_doc = etree.parse(str(xsd_path))
            xmlschema = etree.XMLSchema(xmlschema_doc)
            valid = xmlschema.validate(xml_doc)
            if not valid:
                return False, f"XML fails XSD validation: {xmlschema.error_log.filter_from_errors()[0] if xmlschema.error_log else 'unknown error'}"
            return True, "XML valid against XSD"
        except Exception as e:
            return False, f"XML validation error: {e}"
    else:
        return True, "XML exists (no XSD provided)"

def validate_pdf_basic(file_path, min_pages=1):
    p = Path(file_path)
    if not p.exists():
        return False, f"PDF not found: {file_path}"
    try:
        from PyPDF2 import PdfReader
    except Exception as e:
        return False, f"PyPDF2 not installed: {e}"
    try:
        reader = PdfReader(str(p))
        n = len(reader.pages)
        if n < min_pages:
            return False, f"PDF has {n} pages (<{min_pages})"
        # Heuristic: check for logo usage by searching text for org name — non-definitive
        text = ""
        for i in range(min(n, 3)):
            try:
                text += reader.pages[i].extract_text() or ""
            except Exception:
                pass
        if "BillGenerator" not in text and "Government" not in text:
            return True, f"PDF pages OK but header/footer text heuristic not found (this may be acceptable)"
        return True, "PDF OK"
    except Exception as e:
        return False, f"PDF validation error: {e}"

if __name__ == "__main__":
    # simple CLI: python validate_output.py <type> <file> [xsd] [headers comma separated]
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("type", choices=["csv","xml","pdf"])
    ap.add_argument("file")
    ap.add_argument("--xsd", default=None)
    ap.add_argument("--headers", default=None, help="comma separated headers for csv")
    args = ap.parse_args()
    if args.type == "csv":
        headers = args.headers.split(",") if args.headers else []
        ok, msg = validate_csv(args.file, headers)
    elif args.type == "xml":
        ok, msg = validate_xml(args.file, args.xsd)
    else:
        ok, msg = validate_pdf_basic(args.file)
    print("OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 2)