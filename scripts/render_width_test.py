import os
import sys

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(base_dir)

    from utils.excel_processor import ExcelProcessor
    from utils.document_generator import DocumentGenerator

    # Pick a representative test file
    test_file = os.path.join(base_dir, 'test_input_files', 'FirstFINALnoExtra.xlsx')
    if not os.path.exists(test_file):
        # Fallback to any available .xlsx in test_input_files
        tif = os.path.join(base_dir, 'test_input_files')
        for fn in os.listdir(tif):
            if fn.lower().endswith(('.xlsx', '.xls')):
                test_file = os.path.join(tif, fn)
                break

    print(f"Using input: {os.path.basename(test_file)}")

    processor = ExcelProcessor(test_file)
    data = processor.process_excel()

    generator = DocumentGenerator(data)
    documents = generator.generate_all_documents()

    out_dir = os.path.join(base_dir, 'GENERATED_FILES', 'width_test')
    os.makedirs(out_dir, exist_ok=True)

    # Save HTML outputs
    for name, html in documents.items():
        html_name = name.lower().replace(' ', '_') + '.html'
        with open(os.path.join(out_dir, html_name), 'w', encoding='utf-8') as f:
            f.write(html)

    # Save PDFs
    pdfs = generator.create_pdf_documents(documents)
    for name, content in pdfs.items():
        with open(os.path.join(out_dir, name), 'wb') as f:
            f.write(content)

    print(f"Outputs written to: {out_dir}")

if __name__ == '__main__':
    main()


