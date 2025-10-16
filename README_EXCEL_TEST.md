# Excel Processing Test

This test processes Excel files and organizes the output in a structured directory format as requested.

## Features

1. **All output in one folder**: Results are saved in the `test_outputs` directory
2. **Separate subfolders for different input files**: Each Excel file gets its own subfolder
3. **Timestamped subfolders**: Multiple runs with the same input are separated by timestamped subfolders
4. **Latest results**: Each file has a `latest` directory with the most recent results

## Directory Structure

```
test_outputs/
├── filename1/                    # Subfolder for each input file
│   ├── 2025-10-16_09-45-02/     # Timestamped results
│   │   └── results.txt          # Processing results
│   └── latest/                  # Symlink to latest results
│       └── results.txt
├── filename2/
│   ├── 2025-10-16_09-45-02/
│   │   └── results.txt
│   └── latest/
│       └── results.txt
├── summary_2025-10-16_09-45-02.txt  # Test summary
```

## How to Run

### Option 1: Using Batch Script (Windows)
Double-click on **[RUN_EXCEL_TEST.bat](file:///c:/Users/Rajkumar/BillGeneratorV01/RUN_EXCEL_TEST.bat)**

### Option 2: Using Shell Script (Unix/Linux/Mac)
Run the following command:
```
./RUN_EXCEL_TEST.sh
```

### Option 3: Direct Python Execution
Run the following command:
```
python test_excel_processing.py
```

## What the Test Does

1. Scans the `INPUT_FILES` directory for Excel files
2. Processes the first 5 Excel files as samples
3. For each file:
   - Lists all sheets in the Excel file
   - Gets the dimensions (rows × columns) of each sheet
   - Saves results in organized directory structure
4. Creates a summary report

## Output Format

Each results file contains:
- File name
- Processing timestamp
- Success status
- List of sheet names
- Dimensions of each sheet (rows × columns)

## Troubleshooting

If you encounter issues:
1. Make sure all dependencies are installed
2. Check that the INPUT_FILES directory contains Excel files
3. Verify that you have read permissions for the input files
4. Check the console output for error messages

The test will automatically open the output directory after completion so you can easily access your results.