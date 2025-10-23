# Bill Generator - Professional Infrastructure Billing System

A comprehensive Streamlit application for generating professional infrastructure billing documents with support for multiple formats and deployment options.

## Features

- **Multiple Input Modes**: Excel upload and online entry
- **Professional Document Generation**: PDF, HTML outputs
- **Batch Processing**: Handle multiple files at once
- **Cloud Deployment Ready**: Configured for Streamlit Cloud and other platforms

## Deployment

### Streamlit Cloud Deployment

1. Fork this repository
2. In Streamlit Cloud, set the main file to `app.py`
3. Use Python version from `runtime.txt` (3.11.9)
4. Dependencies are in `requirements.txt` (single consolidated file)
5. Optional: set `ENABLE_PLAYWRIGHT_PDF=1` if your workspace supports Playwright and its browsers; otherwise PDFs will be generated via pure-Python engines
6. Deploy

### Local Deployment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

To run the full feature app with online entry mode UI:

```bash
streamlit run app.py
```

## Requirements

- Python 3.11+
- See `requirements.txt` for dependencies (minimal, pinned)

## Input files

- Sample Excel files live in `input_files/`
- Batch mode defaults to `input_files/` (Linux-friendly lowercase path)

## Usage

1. Upload an Excel file with Title, Work Order, and Bill Quantity sheets
2. Process the data
3. Generate professional documents
4. Download PDF files

## File Structure

- `app.py`: Streamlit application entrypoint
- `requirements.txt`: Consolidated dependencies for deployment and local development

## License

MIT License

# Enhanced Bill Generator

An advanced Streamlit application for infrastructure billing with dual-mode functionality: Excel upload and online entry.

## 🚀 New Features

### Mode Selection Interface
- **Excel Upload Mode**: Traditional workflow for uploading complete Excel files
- **Online Entry Mode**: Step-by-step web forms for bill quantity entry

### Online Entry Capabilities
1. **Work Order Upload**: Upload Excel files or manually enter project details
2. **Bill Quantity Entry**: Interactive forms for entering quantities with real-time calculations
3. **Extra Items Management**: Add custom items not included in the work order
4. **Document Generation**: Professional PDF creation with existing DocumentGenerator integration

## 📋 Key Enhancements

### User Interface
- **Professional Design**: Modern gradient styling with responsive layout
- **Progress Indicators**: Visual progress tracking for multi-step workflows
- **Interactive Forms**: Dynamic work item management with add/remove functionality
- **Real-time Calculations**: Live bill totals and amount calculations
- **Mobile Responsive**: Optimized for desktop, tablet, and mobile devices

### Functionality
- **Hybrid Architecture**: Maintains existing Excel functionality while adding online capability
- **Session State Management**: Persistent data across steps in online mode
- **Error Handling**: Comprehensive validation and error reporting
- **Data Preview**: Real-time preview of entered data before document generation
- **Download Management**: Multiple download options for generated documents

## 🛠 Technical Architecture

### File Structure
```
enhanced_app.py          # Main application file (38KB, 1,139 lines)
├── Mode Selection       # Choose between Excel upload and online entry
├── Excel Upload Mode    # Existing functionality preserved
├── Online Entry Mode    # New 4-step workflow
│   ├── Step 1: Work Order Upload
│   ├── Step 2: Bill Quantity Entry
│   ├── Step 3: Extra Items (Optional)
│   └── Step 4: Document Generation
└── Document Integration # Compatible with existing DocumentGenerator
```

### Integration Points
- **ExcelProcessor**: Reused for Excel file processing in both modes
- **DocumentGenerator**: Full compatibility maintained for document creation
- **PDFMerger**: Integrated for combining multiple generated documents

## 💻 Installation & Usage

### Prerequisites
- Streamlit
- pandas
- numpy
- openpyxl (for Excel processing)
- Existing utils modules (excel_processor, document_generator, pdf_merger)

### Running the Application
```bash
streamlit run enhanced_app.py
```

### Usage Modes

#### Excel Upload Mode
1. Select "Excel Upload Mode" from the main interface
2. Upload Excel file with required sheets (Title, Work Order, Bill Quantity)
3. Review data preview
4. Generate documents

#### Online Entry Mode
1. Select "Online Entry Mode" from the main interface
2. **Step 1**: Upload work order Excel file OR enter project details manually
3. **Step 2**: Enter quantities for each work item with live calculations
4. **Step 3**: Add extra items (optional)
5. **Step 4**: Review summary and generate documents

## 📊 Features Overview

### Mode Comparison
| Feature | Excel Upload Mode | Online Entry Mode |
|---------|-------------------|-------------------|
| Data Entry | Pre-prepared Excel files | Web forms and inputs |
| Setup Time | Quick (if Excel ready) | Medium (step-by-step) |
| Flexibility | Limited to Excel structure | High customization |
| Best For | Bulk data, recurring bills | One-time bills, custom items |
| Technical Skill | Excel knowledge | Basic computer skills |

### Bill Quantity Entry Features
- **Interactive Forms**: Enter quantities with validation
- **Real-time Calculations**: Live amount calculations as quantities change
- **Summary Dashboard**: Metrics showing items, quantities, and totals
- **Data Validation**: Ensures data integrity before document generation
- **Progress Tracking**: Visual indicators showing completion status

### Extra Items Management
- **Dynamic Addition**: Add unlimited extra items with description, unit, rate, and quantity
- **Edit/Remove**: Modify or remove extra items as needed
- **Cost Calculation**: Automatic amount calculation for extra items
- **Integration**: Seamlessly integrates with main bill calculations

## 🎨 User Interface Elements

### Styling Features
- **Gradient Headers**: Professional blue gradient design
- **Card-based Layout**: Clean, modern card interfaces
- **Progress Circles**: Visual step completion indicators
- **Metric Cards**: Dashboard-style summary displays
- **Responsive Design**: Mobile-optimized layouts
- **Interactive Buttons**: Hover effects and smooth transitions

### Navigation
- **Step-by-step Flow**: Clear progression through online entry steps
- **Breadcrumbs**: Progress indicator showing current step
- **Back/Forward Navigation**: Easy movement between steps
- **Reset Functionality**: Quick application reset option

## 🔧 Technical Details

### Session State Management
- Persistent data storage across steps
- State validation and error recovery
- Clean state management for new sessions

### Data Processing
- **Excel Integration**: Full compatibility with existing ExcelProcessor
- **Data Validation**: Input validation and error handling
- **Format Conversion**: Automatic conversion between online and Excel formats
- **Document Generation**: Seamless integration with existing DocumentGenerator

### Error Handling
- Comprehensive exception handling
- User-friendly error messages
- Recovery options for common issues
- Logging for debugging

## 📈 Performance Optimizations

### Loading
- Lazy loading of components
- Efficient state management
- Minimal resource usage

### User Experience
- Responsive design patterns
- Progressive enhancement
- Real-time feedback
- Smooth transitions

## 🔒 Data Security & Validation

### Input Validation
- Required field validation
- Numeric input constraints
- Data type verification
- Format validation

### File Handling
- Secure temporary file management
- Automatic cleanup
- Error recovery

## 📱 Mobile Compatibility

### Responsive Design
- Mobile-optimized layouts
- Touch-friendly interfaces
- Adaptive column sizing
- Collapsible sections

## 🚀 Future Enhancements

### Potential Additions
- **Bulk Import**: CSV import for work items
- **Templates**: Predefined project templates
- **History**: Session history and recovery
- **Export Options**: Additional export formats
- **User Preferences**: Customizable settings
- **Batch Processing**: Multiple bill processing

### Integration Opportunities
- **Database Integration**: Store frequently used data
- **API Endpoints**: External system integration
- **Cloud Storage**: Cloud-based file management
- **Notifications**: Email/SMS notifications

## 📝 Changelog

### Version 2.0 (Enhanced)
- ✅ Added mode selection interface
- ✅ Implemented online entry workflow
- ✅ Added bill quantity entry forms
- ✅ Created extra items management
- ✅ Enhanced UI/UX design
- ✅ Added progress tracking
- ✅ Implemented responsive design
- ✅ Maintained DocumentGenerator compatibility

### Version 1.0 (Original)
- Excel upload functionality
- Document generation
- PDF merging capabilities

## 🤝 Contributing

### Development Guidelines
1. Maintain compatibility with existing DocumentGenerator
2. Follow existing code patterns and naming conventions
3. Ensure mobile responsiveness
4. Add comprehensive error handling
5. Include user-friendly feedback

### Testing
- Test both Excel and online modes
- Verify document generation
- Check mobile responsiveness
- Validate error handling

## 📞 Support

### Common Issues
1. **File Upload Errors**: Check file format and size
2. **Generation Failures**: Verify all required data is entered
3. **Display Issues**: Try refreshing the browser
4. **Navigation Problems**: Use the reset button to restart

### Troubleshooting
- Check browser console for errors
- Verify all dependencies are installed
- Ensure utils modules are accessible
- Review file permissions

---

## 🎯 Summary

The Enhanced Bill Generator successfully extends the original application with:

- **Dual-mode functionality** preserving existing Excel workflows
- **Interactive online entry** for flexible bill creation
- **Professional UI/UX** with modern, responsive design
- **Real-time calculations** and progress tracking
- **Full compatibility** with existing DocumentGenerator system
- **Comprehensive error handling** and user feedback
- **Mobile optimization** for cross-device usage

This enhancement transforms the bill generator from an Excel-dependent tool into a versatile, user-friendly application suitable for various use cases and skill levels.
