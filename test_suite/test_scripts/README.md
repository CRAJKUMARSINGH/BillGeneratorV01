# Test Scripts

This directory contains all test scripts for the Bill Generator application.

## Test Categories

### Unit Tests
- `test_*.py` - Individual component tests
- `test_excel_processing.py` - Excel file processing tests
- `test_pdf_generation.py` - PDF generation tests
- `test_certificate_ii.py` - Certificate II content tests

### Integration Tests
- `test_enhanced_generation.py` - Document generation tests
- `test_file_processing.py` - End-to-end file processing tests
- `test_online_mode.py` - Online mode functionality tests

### Performance Tests
- `batch_performance_tester.py` - Batch processing performance tests
- `test_performance_improvements.py` - Performance optimization tests

### Validation Tests
- `validate_pdf_quality.py` - PDF output quality validation
- `test_html_pdf_conversion.py` - HTML to PDF conversion tests

## Running Tests

To run a specific test:
```bash
python test_certificate_ii.py
```

To run all tests:
```bash
cd ..
python run_tests.py
```

## Test Script Naming Convention

- `test_*.py` - Standard unit and integration tests
- `*_test.py` - Specialized tests
- `*_test_*.py` - Specific scenario tests
- `batch_*.py` - Batch processing tests
- `comprehensive_*.py` - Comprehensive end-to-end tests
- `simple_*.py` - Simple functionality tests

## Adding New Tests

When adding new test scripts:
1. Follow the existing naming convention
2. Include clear docstrings explaining the test purpose
3. Use appropriate assert statements for validation
4. Handle exceptions gracefully
5. Provide meaningful output for debugging