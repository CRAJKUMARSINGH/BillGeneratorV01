#!/usr/bin/env python3
"""
Debug test to verify the note sheet template loading
"""

import os
from utils.template_renderer import TemplateRenderer

# Print current working directory
print("Current working directory:", os.getcwd())

# Check if templates directory exists
if os.path.exists('templates'):
    print("Templates directory exists")
    files = os.listdir('templates')
    print("Files in templates directory:", files)
else:
    print("Templates directory does not exist")

# Check if note_sheet.html exists
if os.path.exists('templates/note_sheet.html'):
    print("note_sheet.html exists")
    with open('templates/note_sheet.html', 'r') as f:
        content = f.read()
        print("Column widths in template:", 'width: 3mm;' in content, 'width: 37mm;' in content, 'width: 149mm;' in content)
else:
    print("note_sheet.html does not exist")

# Try to load template
try:
    template_renderer = TemplateRenderer()
    print("TemplateRenderer created successfully")
    
    # Try to load the template directly
    template = template_renderer.jinja_env.get_template('note_sheet.html')
    print("note_sheet.html template loaded successfully")
    
    # Print first 500 characters of template
    template_content = template.render()
    print("Template loaded content (first 500 chars):")
    print(template_content[:500])
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()