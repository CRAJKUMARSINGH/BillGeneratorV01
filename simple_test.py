#!/usr/bin/env python3
"""
Simple test to verify PDF generation fixes
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test the imports
try:
    from enhanced_document_generator_fixed import EnhancedDocumentGenerator
    print("✅ EnhancedDocumentGenerator imported successfully")
except Exception as e:
    print(f"❌ Failed to import EnhancedDocumentGenerator: {e}")
    sys.exit(1)

# Test the CSS injection
test_html = """
<html>
<head>
</head>
<body>
    <h1>Test Document</h1>
    <table>
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
        </tr>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
        </tr>
    </table>
</body>
</html>
"""

try:
    generator = EnhancedDocumentGenerator({})
    processed_html = generator._add_print_css(test_html)
    
    # Check if the CSS was added
    if "table-layout: fixed !important" in processed_html:
        print("✅ Print CSS injected successfully")
    else:
        print("❌ Print CSS not injected properly")
        
    if "margin: 10mm !important" in processed_html:
        print("✅ Margin CSS injected successfully")
    else:
        print("❌ Margin CSS not injected properly")
        
    print("🎉 Simple test completed!")
    
except Exception as e:
    print(f"❌ Error during simple test: {e}")
    import traceback
    traceback.print_exc()
