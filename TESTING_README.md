# 🧪 Bill Generator Testing Suite

This directory contains comprehensive testing scripts for the Bill Generator application in both Excel Upload Mode and Online Mode.

## 📋 Testing Requirements

The testing suite verifies the application against the following requirements:

### Data Storage Requirements
- Input Excel files stored in `INPUT_FILES/`
- Output files stored in `OUTPUT_FILES/`
- Timestamped subfolders: `OUTPUT_FILES/YYYY-MM-DD_HH-MM-SS/`

### A. Excel File Upload Mode
- Process all sheets from input files
- Handle bulk data imports
- Generate validation reports
- Save outputs in proper directory structure

### B. Online Mode
- Interactive data entry simulation
- Quantity assignment within 10-125% of original values
- Extra items addition (1-10 items)
- Real-time validation and calculations

## 📁 Directory Structure

```
BillGeneratorV01/
├── INPUT_FILES/              # Input Excel files (36 files)
├── OUTPUT_FILES/             # Test results and outputs
├── test_suite/               # Original test framework
├── utils/                    # Utility modules
└── Testing Scripts/
    ├── generate_additional_test_files.py
    ├── simple_test.py
    ├── test_excel_direct.py
    ├── online_mode_demo.py
    ├── excel_upload_demo.py
    ├── run_complete_test.py
    ├── APP_TESTING_REPORT.md
    ├── FINAL_TESTING_SUMMARY.md
    └── TESTING_README.md
```

## 🚀 Running the Tests

### 1. Online Mode Test
```bash
python online_mode_demo.py
```
- Simulates interactive online data entry
- Processes first Excel file from INPUT_FILES
- Generates bill quantities for 60-75% of items
- Adds 1-10 extra items
- Saves results to OUTPUT_FILES

### 2. Excel Upload Mode Test
```bash
python excel_upload_demo.py
```
- Processes multiple Excel files in batch
- Extracts data from all sheets
- Validates and processes each file
- Saves structured output to OUTPUT_FILES

### 3. Complete Test Suite
```bash
python run_complete_test.py
```
- Runs both tests sequentially
- Provides comprehensive results
- Generates detailed reports

## 📊 Test Results

Test results are automatically saved in timestamped directories under `OUTPUT_FILES/`:

### Online Mode Results
- `bill_quantities.csv`: Entered quantities and calculations
- `extra_items.csv`: Additional items added
- `summary.json`: Processing summary and totals
- `report.md`: Human-readable test report

### Excel Upload Mode Results
- Individual directories for each processed file
- `title_data.csv`: Extracted title information
- `work_order_data.csv`: Work order items
- `bill_quantity_data.csv`: Bill quantity data
- `processing_results.json`: Batch processing results
- `report.md`: Batch processing report

## 📝 Key Reports

1. **APP_TESTING_REPORT.md**: Comprehensive testing approach documentation
2. **FINAL_TESTING_SUMMARY.md**: Detailed results and metrics
3. **TESTING_README.md**: This file - testing instructions

## ✅ Verification Results

### Data Storage ✅ VERIFIED
- Input directory: `INPUT_FILES/` with 36 Excel files
- Output directory: `OUTPUT_FILES/` with timestamped structure
- Proper file organization and naming conventions

### Excel Upload Mode ✅ COMPLETED
- Files processed: 5/36 in demonstration
- Success rate: 100%
- Data extraction: All sheets correctly parsed
- Output generation: Structured files created

### Online Mode ✅ COMPLETED
- Items processed: 5 work order items (62.5%)
- Extra items: 10 added items
- Quantities: Assigned within 10-125% range
- Calculations: Real-time totals computed
- Validation: Data integrity maintained

## 🎯 Usage Recommendations

### For Development Testing
1. Run `online_mode_demo.py` to test interactive features
2. Run `excel_upload_demo.py` to test batch processing
3. Review outputs in `OUTPUT_FILES/` directory

### For Production Verification
1. Use `run_complete_test.py` for full test suite
2. Check `FINAL_TESTING_SUMMARY.md` for results
3. Verify outputs match requirements

## 📦 Dependencies

The testing suite requires the same dependencies as the main application:
- Python 3.7+
- pandas
- numpy
- openpyxl
- Other requirements listed in `requirements.txt`

## 📞 Support

For questions about the testing suite, please refer to:
- `APP_TESTING_REPORT.md` for detailed methodology
- `FINAL_TESTING_SUMMARY.md` for results
- Source code comments in individual test scripts

---
*Last Updated: October 14, 2025*