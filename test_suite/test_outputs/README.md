# Test Outputs

This directory contains all output files and results generated during test execution.

## Directory Structure

- `test_outputs_*/` - Timestamped output directories from comprehensive test runs
- `fixed_output_*/` - Output directories from fixed document generator tests
- `test_all_formats_output/` - Output from multi-format generation tests

## Output Types

### Generated Documents
- **HTML files** - Generated document templates
- **PDF files** - Final PDF documents
- **ZIP files** - Compressed document packages

### Test Reports
- **Summary files** - Test execution summaries
- **Log files** - Detailed test execution logs
- **Comparison reports** - Document comparison results

### Performance Data
- **Timing reports** - Performance measurement results
- **Resource usage** - Memory and CPU utilization data

## Directory Naming Convention

- `test_outputs_YYYYMMDD_HHMMSS` - Timestamped comprehensive test outputs
- `fixed_output_YYYYMMDD_HHMMSS` - Timestamped fixed generator outputs

## Managing Test Outputs

### Automatic Cleanup
Old test output directories can be removed to save space:
```bash
# Remove outputs older than 7 days (example)
find . -name "test_outputs_*" -mtime +7 -exec rm -rf {} +
```

### Manual Organization
For long-term storage of important test results:
1. Copy important output directories to a backup location
2. Rename directories with descriptive names
3. Document the test scenario and results

## Adding New Output Directories

When tests generate new output directories:
1. They will automatically be placed in this directory
2. The directory name should include a timestamp
3. All generated files should be contained within the directory