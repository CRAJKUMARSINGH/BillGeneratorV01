from flask import Flask, render_template, request, send_file, jsonify
import os
import tempfile
import zipfile
from datetime import datetime
import traceback
import io
from werkzeug.utils import secure_filename
from utils.excel_processor import ExcelProcessor
from utils.document_generator import DocumentGenerator
from utils.pdf_merger import PDFMerger
from utils.zip_packager import ZipPackager
import gc

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload Excel files (.xlsx or .xls)'}), 400
    
    try:
        # Save uploaded file temporarily (sanitized name if ever needed later)
        secure_filename(file.filename)
        
        # Process the Excel file
        start_time = datetime.now()
        
        processor = ExcelProcessor(file)
        data = processor.process_excel()
        
        # Generate documents
        generator = DocumentGenerator(data)
        documents = generator.generate_all_documents()
        
        # Create PDFs
        pdf_files = generator.create_pdf_documents(documents)
        
        # Merge PDFs
        merger = PDFMerger()
        merged_pdf = merger.merge_pdfs(pdf_files)
        
        # Create ZIP package
        packager = ZipPackager()
        zip_buffer = packager.create_package(documents, pdf_files, merged_pdf)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Capture counts then clean up memory
        pdf_files_count = len(pdf_files)
        del documents, pdf_files
        gc.collect()
        
        # Generate filename
        project_name = data.get('title_data', {}).get('Project Name', 'Project')
        clean_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"{clean_project_name}_BillingDocs_{timestamp}.zip"
        
        # Save zip to temporary file for download
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        response = {
            'success': True,
            'message': 'Documents generated successfully!',
            'filename': zip_filename,
            'processing_time': round(processing_time, 2),
            'download_url': f'/download/{zip_filename}',
            'file_size': len(zip_buffer.getvalue()),
            'documents_count': pdf_files_count
        }

        return jsonify(response)
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide specific error guidance
        if "sheet_name" in error_msg or "worksheet" in error_msg.lower():
            error_response = {
                'error': 'Missing Required Sheets',
                'message': 'Your Excel file is missing required sheets. Please ensure your file contains: Title, Work Order, Bill Quantity sheets.',
                'details': error_msg
            }
        elif "column" in error_msg.lower() or "key" in error_msg.lower():
            error_response = {
                'error': 'Column Format Issue',
                'message': 'Your Excel file has missing or incorrectly named columns.',
                'details': error_msg
            }
        else:
            error_response = {
                'error': 'Processing Error',
                'message': 'An error occurred while processing your file.',
                'details': error_msg
            }
        
        return jsonify(error_response), 400

@app.route('/download/<filename>')
def download_file(filename):
    try:
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/zip'
        )
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
