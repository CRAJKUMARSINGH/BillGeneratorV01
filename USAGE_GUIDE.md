# Bill Generator V01 - Usage Guide

This application has two modes of operation:

## 🖥️ Desktop Mode (Original Streamlit App)

**For traditional Excel file upload and processing**

### How to Run:
```bash
streamlit run app.py
```

### What it does:
- Upload Excel files with Title, Work Order, Bill Quantity, and Extra Items sheets
- Generates professional billing documents
- Downloads all documents in a ZIP package
- Includes PDF, Word, and HTML formats

### Access:
- Opens automatically in your web browser
- Usually at http://localhost:8501

---

## 🌐 Online Mode (Flask Extension)

**For online bill entry without Excel files**

### How to Run:
```bash
python run_flask.py
```

### What it does:
- Upload work order files
- Enter bill quantities through a web form
- Generate billing documents online
- Download generated documents

### Access:
- Open http://localhost:5000 in your web browser

---

## 📝 File Requirements (Both Modes)

### For Desktop Mode (Excel Upload):
- **Title Sheet**: Project information and metadata
- **Work Order Sheet**: Original planned work items
- **Bill Quantity Sheet**: Actual work completed quantities
- **Extra Items Sheet**: Additional work items (optional)

### For Online Mode (Work Order Upload):
- **Work Order File**: Excel file with work items
- Then enter quantities through the web interface

---

## 🏃‍♂️ Quick Start

1. **For traditional Excel processing**: `streamlit run app.py`
2. **For online bill entry**: `python run_flask.py`

Both applications use the same core processing engine and generate the same professional documents.

---

## 📁 Generated Documents

Both modes generate:
- First Page Summary
- Deviation Statement  
- Final Bill Scrutiny Sheet
- Extra Items Statement
- Certificate II & III
- Combined PDF with all documents
- Multiple formats: PDF, Word, HTML

---

## 🛠️ Troubleshooting

If you get import errors:
1. Make sure you're in the correct directory
2. Check that all required packages are installed
3. For Flask mode, ensure templates and static directories exist

---

## 👥 Credits

**Original Streamlit Application**: Full-featured billing document generator
**Online Extension**: Added by development team for enhanced accessibility
**Initiative by**: Mrs. Premlata Jain, Additional Administrative Officer, PWD, Udaipur
