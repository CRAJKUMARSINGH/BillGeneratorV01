import pandas as pd
from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import os

# Create test data
data = {
    'title_data': {},
    'work_order_data': pd.DataFrame(),
    'bill_quantity_data': pd.DataFrame(),
    'extra_items_data': pd.DataFrame()
}

# Create generator instance
gen = EnhancedDocumentGenerator(data)

# Simple HTML with table
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Table PDF</title>
</head>
<body>
    <h1>Test Document with Table</h1>
    <table border="1">
        <thead>
            <tr>
                <th>Item</th>
                <th>Description</th>
                <th>Quantity</th>
                <th>Rate</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td>Excavation in Hard Rock</td>
                <td>150.50</td>
                <td>1500.00</td>
                <td>225750.00</td>
            </tr>
            <tr>
                <td>2</td>
                <td>Providing and Laying Cement Concrete M20</td>
                <td>85.25</td>
                <td>4500.00</td>
                <td>383625.00</td>
            </tr>
            <tr>
                <td>E1</td>
                <td>Additional Survey Work</td>
                <td>1.00</td>
                <td>15000.00</td>
                <td>15000.00</td>
            </tr>
        </tbody>
    </table>
</body>
</html>
"""

# Generate PDF
output_path = "test_table_output.pdf"
result = gen._generate_pdf_reportlab(html_content, output_path)

print(f"PDF generation result: {result}")
if result and os.path.exists(output_path):
    file_size = os.path.getsize(output_path)
    print(f"PDF created successfully. File size: {file_size} bytes")
else:
    print("PDF generation failed")