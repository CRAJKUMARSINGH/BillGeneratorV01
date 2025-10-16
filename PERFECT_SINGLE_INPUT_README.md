# Perfect Single Input Bill Generator

This application is optimized specifically for processing single Excel files with maximum efficiency and user-friendly interface.

## Features

### 🎯 Single File Focus
- Streamlined interface designed for processing one file at a time
- Optimized performance for single file operations
- Simplified workflow with clear steps

### 📄 Complete Document Generation
- Generates all document formats: HTML, PDF, and DOC
- Professional templates for government billing documents
- High-quality PDF generation using Playwright

### 🚀 Enhanced Performance
- Fast processing with optimized memory usage
- Real-time progress indicators
- Efficient file handling

### 🎨 Modern Interface
- Clean, professional blue color scheme (#0ea5e9)
- Responsive design that works on all devices
- Intuitive user experience

## How to Use

### Option 1: Windows
Double-click on **[LAUNCH_PERFECT_SINGLE_INPUT.bat](file:///c:/Users/Rajkumar/BillGeneratorV01/LAUNCH_PERFECT_SINGLE_INPUT.bat)**

### Option 2: Unix/Linux/Mac
Run the following command:
```bash
./LAUNCH_PERFECT_SINGLE_INPUT.sh
```

### Option 3: Direct Execution
Run the following command:
```bash
streamlit run perfect_single_input_app.py --server.port=8506
```

## Workflow

1. **Upload Excel File**
   - Click the upload area or drag and drop your Excel file
   - Supported formats: .xlsx, .xls
   - File should contain Title, Work Order, and Bill Quantity sheets

2. **Review Data**
   - Preview processed data in expandable sections
   - Verify project information, work order items, and bill quantities

3. **Generate Documents**
   - Click "Generate All Documents" button
   - Watch real-time progress indicators
   - See success messages for each document type

4. **Download Files**
   - Access all generated documents in the download section
   - Download individual files by format (HTML, PDF, DOC)
   - Download complete ZIP package with all formats

## Document Types Generated

### HTML Documents
- First_Page_Summary.html
- Deviation_Statement.html
- Final_Bill_Scrutiny_Sheet.html
- Extra_Items_Statement.html
- Certificate_II.html
- Certificate_III.html

### PDF Documents
- First Page Summary.pdf
- Deviation Statement.pdf
- Final Bill Scrutiny Sheet.pdf
- Extra Items Statement.pdf
- Certificate II.pdf
- Certificate III.pdf
- Merged_Documents.pdf

### DOC Documents
- First_Page_Summary.docx
- Deviation_Statement.docx
- Final_Bill_Scrutiny_Sheet.docx
- Extra_Items_Statement.docx
- Certificate_II.docx
- Certificate_III.docx

### ZIP Package
- All_Documents.zip (contains all formats)

## Performance Metrics

The application provides real-time performance metrics in the sidebar:
- Document counts by type
- Total file size
- Processing status

## Technical Features

### Optimized Processing
- Efficient memory management
- Fast Excel file parsing
- Parallel document generation where possible

### Error Handling
- Comprehensive error reporting
- Graceful failure recovery
- User-friendly error messages

### Session Management
- Automatic session state management
- Data persistence during processing
- Clean reset functionality

## Requirements

- Python 3.7 or higher
- All dependencies listed in requirements.txt
- Playwright browser dependencies (automatically installed)

## Port Information

The application runs on port **8506** to avoid conflicts with other applications:
- http://localhost:8506

## Troubleshooting

### Common Issues
1. **File upload fails**: Ensure file is not open in another program
2. **Document generation fails**: Check that all required sheets are present
3. **Download issues**: Verify file permissions and disk space

### Reset Application
Use the "Reset Generator" button in the sidebar to clear all data and start fresh.

## Benefits Over Original App

1. **Simplified Interface**: Focused on single file processing
2. **Better Performance**: Optimized for the most common use case
3. **Enhanced UX**: Modern design with clear feedback
4. **Complete Output**: Generates all document formats
5. **Real-time Metrics**: Performance monitoring
6. **Responsive Design**: Works on all device sizes