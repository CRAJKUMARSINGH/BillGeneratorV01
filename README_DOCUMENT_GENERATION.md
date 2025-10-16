# Document Generation Scripts

This project includes scripts to generate all document formats (HTML, PDF, DOC) and save them in organized directories.

## Files Created

1. **[GENERATE_ALL_DOCUMENTS.bat](file:///c:/Users/Rajkumar/BillGeneratorV01/GENERATE_ALL_DOCUMENTS.bat)** - Windows batch script to generate all document formats
2. **[generate_all_documents.py](file:///c:/Users/Rajkumar/BillGeneratorV01/generate_all_documents.py)** - Python script that generates HTML, PDF, and DOC files
3. **[🚀_LAUNCH_APP.bat](file:///c:/Users/Rajkumar/BillGeneratorV01/🚀_LAUNCH_APP.bat)** - Original application launch script

## How to Generate Documents

### Option 1: Using the Batch Script (Recommended)
Double-click on **[GENERATE_ALL_DOCUMENTS.bat](file:///c:/Users/Rajkumar/BillGeneratorV01/GENERATE_ALL_DOCUMENTS.bat)** to generate all document formats.

### Option 2: Using Command Line
Run the following command in the terminal:
```
python generate_all_documents.py
```

## Output Structure

After running the script, all documents will be generated in the `output` folder with the following structure:

```
output/
├── html/              # HTML files
│   ├── Certificate_II.html
│   ├── Certificate_III.html
│   ├── Deviation_Statement.html
│   ├── Extra_Items_Statement.html
│   ├── Final_Bill_Scrutiny_Sheet.html
│   └── First_Page_Summary.html
├── pdf/               # PDF files
│   ├── Certificate II.pdf
│   ├── Certificate III.pdf
│   ├── Deviation Statement.pdf
│   ├── Extra Items Statement.pdf
│   ├── Final Bill Scrutiny Sheet.pdf
│   ├── First Page Summary.pdf
│   └── Merged_Documents.pdf
├── doc/               # DOC files
│   ├── Certificate II.docx
│   ├── Certificate III.docx
│   ├── Deviation Statement.docx
│   ├── Extra Items Statement.docx
│   ├── Final Bill Scrutiny Sheet.docx
│   └── First Page Summary.docx
└── All_Documents.zip  # ZIP package with all formats
```

## Troubleshooting

If you don't see any PDF or DOC output files:

1. Make sure all dependencies are installed by running the batch script
2. Check that Playwright browsers are installed (happens automatically)
3. Verify that the output folder is created after running the script
4. If there are errors, check the console output for error messages

## Viewing Documents

After generation, you can:
- Open HTML files directly in any web browser
- Open PDF files with any PDF reader
- Open DOC files with Microsoft Word or compatible software
- Extract the ZIP file to get all formats at once

The script will automatically open the output folder after generation so you can easily access your documents.