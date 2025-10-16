#!/usr/bin/env python3
"""
Test the margin fix verification
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Test the margin parsing with our HTML file
with open('test_final_bill_scrutiny_output.html', 'r') as f:
    html_content = f.read()

print("HTML content loaded")

# Test the improved margin parsing logic
from bs4 import BeautifulSoup
from reportlab.lib.units import mm
import re

# Parse HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Extract margins using the improved logic
left_margin = 14*mm
right_margin = 14*mm
top_margin = 14*mm
bottom_margin = 10*mm

# Look for @page rule with margin settings - improved regex with better pattern matching
style_tags = soup.find_all('style')
for style_tag in style_tags:
    style_content = style_tag.get_text()
    print(f"Style content: {style_content}")
    
    # Find @page rules with better pattern matching
    page_rule_matches = re.finditer(r'@page\s*{[^}]*margin\s*:\s*([^;}]+)[^}]*}', style_content)
    for match in page_rule_matches:
        margin_values = match.group(1).strip()
        print(f"Found margin values: '{margin_values}'")
        # Parse different margin formats
        if ' ' in margin_values:
            # Format: "15mm 10mm" (top/right/bottom/left - CSS shorthand)
            parts = margin_values.split()
            if len(parts) == 2:
                try:
                    # 2 values: top/bottom right/left
                    top_margin_val = float(parts[0].replace('mm', ''))
                    right_margin_val = float(parts[1].replace('mm', ''))
                    top_margin = top_margin_val * mm
                    right_margin = right_margin_val * mm
                    bottom_margin = top_margin_val * mm  # Same as top
                    left_margin = right_margin_val * mm  # Same as right
                    print(f"Parsed 2-value margins: top={top_margin_val}mm, right={right_margin_val}mm")
                except Exception as e:
                    print(f"Error parsing 2-value margins: {e}")
            elif len(parts) == 3:
                # 3 values: top left/right bottom
                try:
                    top_margin_val = float(parts[0].replace('mm', ''))
                    right_margin_val = float(parts[1].replace('mm', ''))
                    bottom_margin_val = float(parts[2].replace('mm', ''))
                    top_margin = top_margin_val * mm
                    right_margin = right_margin_val * mm
                    bottom_margin = bottom_margin_val * mm
                    left_margin = right_margin_val * mm  # Same as right
                    print(f"Parsed 3-value margins: top={top_margin_val}mm, right={right_margin_val}mm, bottom={bottom_margin_val}mm")
                except Exception as e:
                    print(f"Error parsing 3-value margins: {e}")
            elif len(parts) == 4:
                # 4 values: top right bottom left
                try:
                    top_margin_val = float(parts[0].replace('mm', ''))
                    right_margin_val = float(parts[1].replace('mm', ''))
                    bottom_margin_val = float(parts[2].replace('mm', ''))
                    left_margin_val = float(parts[3].replace('mm', ''))
                    top_margin = top_margin_val * mm
                    right_margin = right_margin_val * mm
                    bottom_margin = bottom_margin_val * mm
                    left_margin = left_margin_val * mm
                    print(f"Parsed 4-value margins: top={top_margin_val}mm, right={right_margin_val}mm, bottom={bottom_margin_val}mm, left={left_margin_val}mm")
                except Exception as e:
                    print(f"Error parsing 4-value margins: {e}")
        else:
            # Format: "15mm" (all margins same)
            try:
                margin_val = float(margin_values.replace('mm', ''))
                top_margin = right_margin = bottom_margin = left_margin = margin_val * mm
                print(f"Parsed 1-value margins: all={margin_val}mm")
            except Exception as e:
                print(f"Error parsing 1-value margins: {e}")

print(f"Final parsed margins:")
print(f"  Top: {top_margin/mm}mm")
print(f"  Right: {right_margin/mm}mm")
print(f"  Bottom: {bottom_margin/mm}mm")
print(f"  Left: {left_margin/mm}mm")

# Check if margins are correct
expected_top = 15
expected_right = 10
expected_bottom = 15
expected_left = 10

if (abs(top_margin/mm - expected_top) < 0.1 and 
    abs(right_margin/mm - expected_right) < 0.1 and
    abs(bottom_margin/mm - expected_bottom) < 0.1 and
    abs(left_margin/mm - expected_left) < 0.1):
    print("✅ Margin parsing is working correctly!")
    sys.exit(0)
else:
    print("❌ Margin parsing is not working correctly!")
    sys.exit(1)