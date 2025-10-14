# Test Inputs

This directory contains all input files used for testing the Bill Generator application.

## Directory Structure

- [test_input_files/](file:///c%3A/Users/Rajkumar/BillGeneratorV01/test_suite/test_inputs/test_input_files/) - Original test Excel files
- [unified_test_inputs/](file:///c%3A/Users/Rajkumar/BillGeneratorV01/test_suite/test_inputs/unified_test_inputs/) - Consolidated test files following project guidelines

## Test Input Files

### File Types
All test input files are Excel documents (.xlsx) with the following sheet structure:
- **Title** - Project and contract information
- **Work Order** - Work items with quantities and rates
- **Bill Quantity** - Actual quantities for billing
- **Extra Items** (optional) - Additional work items

### File Naming Convention
- `*Final*` - Final bill documents
- `*Running*` - Running bill documents
- `*NoExtra*` - Documents without extra items
- `*VidExtra*` - Documents with extra items
- `new_t01plus*` - Special test cases

## Adding New Test Inputs

When adding new test input files:
1. Ensure they follow the required Excel sheet structure
2. Use descriptive filenames that indicate the test scenario
3. Place them in the appropriate subdirectory
4. Update any relevant test scripts to use the new files

## Test Coverage

The current test inputs cover:
- Different bill types (Final, Running)
- Various work item configurations
- Extra items scenarios
- Edge cases and special formatting
- Hierarchical data structures