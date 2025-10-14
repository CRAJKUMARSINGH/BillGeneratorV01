# Test Suite

This directory contains all test-related files for the Bill Generator application, organized into three main subdirectories:

## Directory Structure

- [test_scripts/](file:///c%3A/Users/Rajkumar/BillGeneratorV01/test_suite/test_scripts/) - All test scripts and testing utilities
- [test_inputs/](file:///c%3A/Users/Rajkumar/BillGeneratorV01/test_suite/test_inputs/) - Test input files (Excel documents)
- [test_outputs/](file:///c%3A/Users/Rajkumar/BillGeneratorV01/test_suite/test_outputs/) - Test output files and results

## Running Tests

To run all tests:
```bash
python run_tests.py
```

To run a specific test:
```bash
cd test_scripts
python test_certificate_ii.py
```

## Test Organization

The test suite is organized to make it easy to find and run specific tests:

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: End-to-end workflow testing
3. **Performance Tests**: Speed and efficiency testing
4. **Validation Tests**: Output quality verification

## Adding New Tests

To add new tests:
1. Place test scripts in the [test_scripts/](file:///c%3A/Users/Rajkumar/BillGeneratorV01/test_suite/test_scripts/) directory
2. Add test input files to the appropriate subdirectory in [test_inputs/](file:///c%3A/Users/Rajkumar/BillGeneratorV01/test_suite/test_inputs/)
3. Test outputs will be generated in [test_outputs/](file:///c%3A/Users/Rajkumar/BillGeneratorV01/test_suite/test_outputs/) during execution