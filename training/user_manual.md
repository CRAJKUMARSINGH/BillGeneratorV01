# BillGenerator User Manual

## Table of Contents
1. Introduction
2. Installation
3. Getting Started
4. Generating Bills
5. Exporting and Validating Outputs
6. Troubleshooting
7. FAQs

## 1. Introduction

BillGenerator is a powerful tool for generating infrastructure bills in statutory-compliant formats. It supports PDF, XML, and CSV output formats.

## 2. Installation

### Requirements
- Python 3.8 or higher
- Required Python packages (see requirements.txt)

### Installation Steps
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`

## 3. Getting Started

1. Prepare your input Excel file with the required format
2. Launch the application
3. Upload your Excel file
4. Configure output options
5. Generate bills

## 4. Generating Bills

1. Upload your Excel file using the file uploader
2. Select the output format (PDF, XML, CSV)
3. Click "Generate Bills"
4. Download the generated files

## 5. Exporting and Validating Outputs

The application automatically validates generated outputs against statutory requirements. You can also manually validate outputs using the validation tools.

## 6. Troubleshooting

Common issues and solutions:
- File not found: Check file paths and permissions
- Format errors: Ensure input file matches required format
- Memory issues: Process smaller batches of files

## 7. FAQs

Q: What formats are supported?
A: PDF, XML, and CSV formats are supported.

Q: Can I customize the output templates?
A: Yes, templates can be customized in the templates directory.