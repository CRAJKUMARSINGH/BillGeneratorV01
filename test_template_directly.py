from jinja2 import Environment, FileSystemLoader
import os

# Sample data
template_data = {
    'data': {
        'item_list': [
            {
                'serial_no': 'E1',
                'remark': 'Urgent repair work',
                'description': 'Emergency Repairs',
                'quantity': '1.00',
                'unit': 'Lot',
                'rate': '5000.00',
                'amount': '5000.00'
            },
            {
                'serial_no': 'E2',
                'remark': 'Extra light fittings as per client request',
                'description': 'Additional Light Fittings',
                'quantity': '5.00',
                'unit': 'Nos',
                'rate': '200.00',
                'amount': '1000.00'
            }
        ]
    }
}

# Initialize template environment
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

# Load and render template
template = env.get_template('extra_items.html')
html = template.render(**template_data)

# Print result
print("Generated HTML:")
print(html)

# Save to file
with open("test_direct_output.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Saved to test_direct_output.html")