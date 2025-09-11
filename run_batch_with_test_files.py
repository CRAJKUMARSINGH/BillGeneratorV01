#!/usr/bin/env python3
"""
Batch runner: Process all Excel files in test_input_files/ and generate output ZIPs in out/

Usage:
  python run_batch_with_test_files.py
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

import pandas as pd  # noqa: F401  (ensures pandas engine plugins are registered)

from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator
from utils.pdf_merger import PDFMerger
from utils.zip_packager import ZipPackager


def process_file(input_path: Path, output_dir: Path) -> Path:
    start = time.time()
    processor = ExcelProcessor(str(input_path))
    data = processor.process_excel()

    generator = DocumentGenerator(data)
    documents = generator.generate_all_documents()
    pdf_files = generator.create_pdf_documents(documents)
    merger = PDFMerger()
    merged_pdf = merger.merge_pdfs(pdf_files)
    packager = ZipPackager()
    zip_buffer = packager.create_package(documents, pdf_files, merged_pdf)

    project_name = data.get('title_data', {}).get('Project Name', input_path.stem)
    safe_name = "".join(c for c in project_name if c.isalnum() or c in (" ", "-", "_")).strip() or input_path.stem
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_name = f"{safe_name}_BillingDocs_{timestamp}.zip"
    out_path = output_dir / out_name
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(zip_buffer.getvalue())

    elapsed = time.time() - start
    print(f"✅ Processed: {input_path.name} -> {out_path} ({elapsed:.2f}s)")
    return out_path


def main():
    base_dir = Path(__file__).resolve().parent
    input_dir = base_dir / 'test_input_files'
    output_dir = base_dir / 'out'

    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        sys.exit(1)

    excel_paths = sorted([p for p in input_dir.glob('*.xlsx')])
    if not excel_paths:
        print(f"❌ No .xlsx files found in {input_dir}")
        sys.exit(1)

    print(f"🚀 Running batch on {len(excel_paths)} file(s) from {input_dir} -> {output_dir}")
    successes = 0
    failures = []

    for path in excel_paths:
        try:
            process_file(path, output_dir)
            successes += 1
        except Exception as e:
            print(f"❌ Failed: {path.name} -> {e}")
            failures.append((path.name, str(e)))

    print("\n📊 Batch Summary")
    print(f"  ✅ Succeeded: {successes}")
    print(f"  ❌ Failed: {len(failures)}")
    if failures:
        for name, err in failures:
            print(f"   - {name}: {err}")

    print(f"\n📂 Outputs saved to: {output_dir}")


if __name__ == '__main__':
    main()

