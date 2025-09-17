from flask import Flask, render_template, request, send_file, flash, jsonify
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
        # Save uploaded file temporarily
        filename = secure_filename(file.filename)
        
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
        
        # Clean up memory
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
        
        return jsonify({
            'success': True,
            'message': 'Documents generated successfully!',
            'filename': zip_filename,
            'processing_time': round(processing_time, 2),
            'download_url': f'/download/{zip_filename}',
            'file_size': len(zip_buffer.getvalue()),
            'documents_count': len(documents) if 'documents' in locals() else 0
        })
        
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

@app.route('/quantity-filling')
def quantity_filling():
    """Display quantity filling interface for work order items"""
    try:
        # Use a simpler approach - create sample data directly
        work_items = [
            {'item_no': '1', 'description': 'Rewiring of light point/fan point/exhaust fan point', 'unit': 'Nos', 'rate': 150.00},
            {'item_no': '2', 'description': 'Rewiring of 3/5 pin 6 amp. Light plug point with PVC conduit', 'unit': 'Nos', 'rate': 200.00},
            {'item_no': '3', 'description': 'Installation of LED tube light 20W', 'unit': 'Nos', 'rate': 300.00},
            {'item_no': '4', 'description': 'Installation of ceiling fan', 'unit': 'Nos', 'rate': 450.00},
            {'item_no': '5', 'description': 'Installation of exhaust fan', 'unit': 'Nos', 'rate': 250.00}
        ]
        
        # Sample project data
        title_data = {
            'Name of Work': 'Electrical Installation Work',
            'Agreement No.': 'AGR/2024/001',
            'Reference to work order or Agreement': 'WO/2024/001'
        }
        
        # Prepare project data as JSON for form submission
        import json
        project_data_json = json.dumps({
            'title_data': title_data,
            'work_order_data': work_items,
            'bill_quantity_data': [],
            'extra_items_data': []
        })
        
        return render_template('quantity_filling.html', 
                             title_data=title_data,
                             work_items=work_items,
                             project_data_json=project_data_json)
            
    except Exception as e:
        return jsonify({'error': f'Error loading quantity filling interface: {str(e)}'}), 500

@app.route('/process-quantities', methods=['POST'])
def process_quantities():
    """Process filled quantities and generate documents"""
    try:
        # Get form data
        project_data_json = request.form.get('project_data')
        if not project_data_json:
            return jsonify({'error': 'No project data provided'}), 400
        
        import json
        project_data = json.loads(project_data_json)
        
        # Extract quantities and rates from form
        quantities = {}
        rates = {}
        
        for key, value in request.form.items():
            if key.startswith('quantity_'):
                index = key.replace('quantity_', '')
                quantities[int(index)] = float(value) if value else 0
            elif key.startswith('rate_'):
                index = key.replace('rate_', '')
                rates[int(index)] = float(value) if value else 0
        
        # Validate rates (cannot exceed work order rates)
        work_order_data = project_data['work_order_data']
        validation_errors = []
        
        for index, rate in rates.items():
            if index < len(work_order_data):
                original_rate = work_order_data[index].get('Rate', 0)
                if rate > original_rate:
                    validation_errors.append(f"Item {index + 1}: Rate {rate} exceeds work order rate {original_rate}")
        
        if validation_errors:
            return jsonify({
                'error': 'Rate validation failed',
                'details': validation_errors
            }), 400
        
        # Update work order data with filled quantities and modified rates
        updated_work_order_data = []
        for i, item in enumerate(work_order_data):
            updated_item = item.copy()
            updated_item['Quantity Since'] = quantities.get(i, 0)
            updated_item['Quantity Upto'] = quantities.get(i, 0)
            updated_item['Rate'] = rates.get(i, item.get('Rate', 0))
            updated_work_order_data.append(updated_item)
        
        # Create updated data structure
        updated_data = {
            'title_data': project_data['title_data'],
            'work_order_data': pd.DataFrame(updated_work_order_data),
            'bill_quantity_data': pd.DataFrame(project_data['bill_quantity_data']),
            'extra_items_data': pd.DataFrame(project_data['extra_items_data'])
        }
        
        # Generate documents
        start_time = datetime.now()
        
        generator = DocumentGenerator(updated_data)
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
        
        # Clean up memory
        del documents, pdf_files
        gc.collect()
        
        # Generate filename
        project_name = updated_data.get('title_data', {}).get('Name of Work', 'Project')
        clean_project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).rstrip()[:20]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"{clean_project_name}_QuantityFilled_{timestamp}.zip"
        
        # Save zip to temporary file for download
        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())
        
        return jsonify({
            'success': True,
            'message': 'Documents generated successfully from filled quantities!',
            'filename': zip_filename,
            'processing_time': round(processing_time, 2),
            'download_url': f'/download/{zip_filename}',
            'file_size': len(zip_buffer.getvalue()),
            'documents_count': len(documents) if 'documents' in locals() else 0,
            'filled_items': len([q for q in quantities.values() if q > 0]),
            'rate_modifications': len([r for i, r in rates.items() if r < work_order_data[i].get('Rate', 0)])
        })
        
    except Exception as e:
        error_msg = str(e)
        return jsonify({
            'error': 'Processing Error',
            'message': 'An error occurred while processing your filled quantities.',
            'details': error_msg
        }), 400

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
