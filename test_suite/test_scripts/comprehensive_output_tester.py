#!/usr/bin/env python3
"""
Comprehensive Output Tester for Bill Generator V01
Tests all templates and generates comparison reports
"""

import os
import sys
import pandas as pd
import json
from datetime import datetime, date
from pathlib import Path
import logging
from output_manager import OutputManager

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator
from utils.excel_processor import ExcelProcessor

class ComprehensiveOutputTester:
    """Comprehensive testing and comparison system for bill generator outputs"""
    
    def __init__(self):
        self.output_manager = OutputManager()
        self.test_results = []
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for testing"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('comprehensive_test.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_sample_data(self):
        """Create comprehensive sample data for testing all templates"""
        sample_data = {
            'title_data': {
                'work_order_no': 'WO/2025/001',
                'contractor_name': 'RAJKUMAR SINGH CHAUHAN',
                'project_title': 'Infrastructure Development Project',
                'location': 'Test Location, City',
                'date': datetime.now().strftime('%d-%m-%Y'),
                'client_name': 'Government Department',
                'client_address': 'Government Office, City'
            },
            'work_order_data': pd.DataFrame({
                'S. No.': [1, 2, 3, 4, 5],
                'Description': [
                    'Excavation for foundation',
                    'Concrete work for foundation',
                    'Steel reinforcement work',
                    'Brick masonry work',
                    'Plastering work'
                ],
                'Unit': ['Cum', 'Cum', 'Kg', 'Sqm', 'Sqm'],
                'Quantity Since': [10.5, 8.2, 150.0, 25.0, 30.0],
                'Quantity Upto': [12.0, 9.5, 175.0, 28.0, 32.0],
                'Rate': [500.0, 1200.0, 45.0, 200.0, 150.0],
                'Amount Upto': [6000.0, 11400.0, 7875.0, 5600.0, 4800.0],
                'Amount Since': [5250.0, 9840.0, 6750.0, 5000.0, 4500.0],
                'Remarks': ['Completed', 'In Progress', 'Completed', 'Pending', 'Completed']
            }),
            'bill_quantity_data': pd.DataFrame({
                'S. No.': [1, 2, 3, 4, 5],
                'Description': [
                    'Excavation for foundation',
                    'Concrete work for foundation', 
                    'Steel reinforcement work',
                    'Brick masonry work',
                    'Plastering work'
                ],
                'Unit': ['Cum', 'Cum', 'Kg', 'Sqm', 'Sqm'],
                'Quantity Since': [10.5, 8.2, 150.0, 25.0, 30.0],
                'Quantity Upto': [12.0, 9.5, 175.0, 28.0, 32.0],
                'Rate': [500.0, 1200.0, 45.0, 200.0, 150.0],
                'Amount Upto': [6000.0, 11400.0, 7875.0, 5600.0, 4800.0],
                'Amount Since': [5250.0, 9840.0, 6750.0, 5000.0, 4500.0],
                'Remarks': ['Completed', 'In Progress', 'Completed', 'Pending', 'Completed']
            }),
            'extra_items_data': pd.DataFrame({
                'S. No.': [1, 2, 3],
                'Description': [
                    'Additional excavation work',
                    'Extra concrete work',
                    'Additional steel work'
                ],
                'Unit': ['Cum', 'Cum', 'Kg'],
                'Quantity': [5.0, 3.0, 25.0],
                'Rate': [600.0, 1300.0, 50.0],
                'Amount': [3000.0, 3900.0, 1250.0],
                'Remarks': ['Extra work', 'Additional work', 'Extra work']
            })
        }
        return sample_data
    
    def test_template_generation(self, template_name, data):
        """Test generation of a specific template"""
        try:
            generator = EnhancedDocumentGenerator(data)
            
            # Generate HTML using the correct method
            html_content = None
            if template_name == 'first_page':
                html_content = generator._generate_first_page()
            elif template_name == 'extra_items':
                html_content = generator._generate_extra_items_statement()
            elif template_name == 'deviation_statement':
                html_content = generator._generate_deviation_statement()
            elif template_name == 'certificate_ii':
                html_content = generator._generate_certificate_ii()
            elif template_name == 'certificate_iii':
                html_content = generator._generate_certificate_iii()
            elif template_name == 'note_sheet':
                html_content = generator._generate_final_bill_scrutiny()
            else:
                # Try to render using template system
                html_content = generator._render_template(template_name)
            
            # Generate PDF (if possible)
            pdf_path = None
            if html_content:
                try:
                    # Create a temporary file for PDF generation
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                        f.write(html_content)
                        temp_html_path = f.name
                    
                    # Generate PDF
                    pdf_filename = f"{template_name}.pdf"
                    pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)
                    
                    if generator.generate_pdf_fixed(html_content, pdf_path):
                        self.logger.info(f"Generated PDF: {pdf_path}")
                    else:
                        pdf_path = None
                        self.logger.warning(f"PDF generation failed for {template_name}")
                    
                    # Clean up temp HTML file
                    os.unlink(temp_html_path)
                    
                except Exception as e:
                    self.logger.warning(f"PDF generation failed for {template_name}: {e}")
                    pdf_path = None
            
            return {
                'template': template_name,
                'html_content': html_content,
                'pdf_path': pdf_path,
                'success': html_content is not None,
                'error': None
            }
        except Exception as e:
            self.logger.error(f"Template generation failed for {template_name}: {e}")
            return {
                'template': template_name,
                'html_content': None,
                'pdf_path': None,
                'success': False,
                'error': str(e)
            }
    
    def run_comprehensive_tests(self):
        """Run comprehensive tests on all templates"""
        self.logger.info("Starting comprehensive output testing...")
        
        # Create output folder for this test run
        output_folder = self.output_manager.create_output_folder(
            "comprehensive_test", 
            f"test_run_{datetime.now().strftime('%H%M%S')}"
        )
        
        # Create sample data
        sample_data = self.create_sample_data()
        
        # Test all available templates
        templates_to_test = [
            'first_page',
            'extra_items', 
            'deviation_statement',
            'certificate_ii',
            'certificate_iii',
            'note_sheet'
        ]
        
        test_results = []
        
        for template in templates_to_test:
            self.logger.info(f"Testing template: {template}")
            result = self.test_template_generation(template, sample_data)
            test_results.append(result)
            
            # Save HTML output
            if result['html_content']:
                html_file = output_folder / "html" / f"{template}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(result['html_content'])
                self.logger.info(f"Saved HTML: {html_file}")
            
            # Save PDF output
            if result['pdf_path'] and os.path.exists(result['pdf_path']):
                pdf_file = output_folder / "pdf" / f"{template}.pdf"
                import shutil
                shutil.copy2(result['pdf_path'], pdf_file)
                self.logger.info(f"Saved PDF: {pdf_file}")
        
        # Generate comparison report
        self.generate_comparison_report(test_results, output_folder)
        
        # Create output summary
        data_summary = {
            'templates_tested': len(templates_to_test),
            'successful_generations': sum(1 for r in test_results if r['success']),
            'failed_generations': sum(1 for r in test_results if not r['success']),
            'test_timestamp': datetime.now().isoformat()
        }
        
        self.output_manager.create_output_summary(output_folder, data_summary)
        
        self.logger.info(f"Comprehensive testing completed. Results saved to: {output_folder}")
        return test_results, output_folder
    
    def generate_comparison_report(self, test_results, output_folder):
        """Generate a comprehensive comparison report"""
        report_file = output_folder / "reports" / "comprehensive_test_report.html"
        
        # Calculate statistics
        total_templates = len(test_results)
        successful = sum(1 for r in test_results if r['success'])
        failed = total_templates - successful
        success_rate = (successful / total_templates) * 100 if total_templates > 0 else 0
        
        # Generate HTML report
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comprehensive Test Report - Bill Generator V01</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }}
        .summary {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #3498db;
            color: white;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
        }}
        .stat-card.success {{ background: #27ae60; }}
        .stat-card.failed {{ background: #e74c3c; }}
        .stat-card.rate {{ background: #f39c12; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }}
        th, td {{
            border: 1px solid #bdc3c7;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background: #34495e;
            color: white;
        }}
        .success {{ color: #27ae60; font-weight: bold; }}
        .failed {{ color: #e74c3c; font-weight: bold; }}
        .error-details {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            padding: 10px;
            border-radius: 4px;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Comprehensive Test Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>📊 Test Summary</h2>
            <p>This report contains the results of comprehensive testing for all Bill Generator V01 templates.</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{total_templates}</h3>
                <p>Templates Tested</p>
            </div>
            <div class="stat-card success">
                <h3>{successful}</h3>
                <p>Successful</p>
            </div>
            <div class="stat-card failed">
                <h3>{failed}</h3>
                <p>Failed</p>
            </div>
            <div class="stat-card rate">
                <h3>{success_rate:.1f}%</h3>
                <p>Success Rate</p>
            </div>
        </div>
        
        <h2>📋 Detailed Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Template</th>
                    <th>Status</th>
                    <th>HTML Generated</th>
                    <th>PDF Generated</th>
                    <th>Error Details</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in test_results:
            status_class = "success" if result['success'] else "failed"
            status_text = "✅ Success" if result['success'] else "❌ Failed"
            html_status = "✅ Yes" if result['html_content'] else "❌ No"
            pdf_status = "✅ Yes" if result['pdf_path'] and os.path.exists(result['pdf_path']) else "❌ No"
            error_details = f'<div class="error-details">{result["error"]}</div>' if result['error'] else "None"
            
            html_content += f"""
                <tr>
                    <td><strong>{result['template']}</strong></td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{html_status}</td>
                    <td>{pdf_status}</td>
                    <td>{error_details}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
        
        <h2>🔧 Recommendations</h2>
        <div class="summary">
            <h3>Based on Test Results:</h3>
            <ul>
                <li><strong>Column Alignment:</strong> Ensure currency and quantity columns are right-aligned</li>
                <li><strong>Deviation Statement:</strong> Verify landscape orientation for 13-column layout</li>
                <li><strong>Extra Items:</strong> Check 7-column layout alignment</li>
                <li><strong>PDF Generation:</strong> Test with different browsers and print settings</li>
            </ul>
        </div>
        
        <h2>📁 Output Files</h2>
        <p>All generated files are saved in the output folder with the following structure:</p>
        <ul>
            <li><strong>HTML files:</strong> Located in the 'html' subfolder</li>
            <li><strong>PDF files:</strong> Located in the 'pdf' subfolder</li>
            <li><strong>Reports:</strong> This report and other analysis files</li>
        </ul>
    </div>
</body>
</html>
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated comparison report: {report_file}")
        return report_file

def main():
    """Main function to run comprehensive tests"""
    tester = ComprehensiveOutputTester()
    
    print("🚀 Starting Comprehensive Output Testing...")
    print("=" * 50)
    
    try:
        test_results, output_folder = tester.run_comprehensive_tests()
        
        print(f"\n✅ Testing completed successfully!")
        print(f"📁 Results saved to: {output_folder}")
        print(f"📊 Success rate: {sum(1 for r in test_results if r['success'])}/{len(test_results)} templates")
        
        # Print summary
        print("\n📋 Template Results:")
        for result in test_results:
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {result['template']}")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
