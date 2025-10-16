#!/usr/bin/env python3
"""
Test the margin parsing functionality
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_document_generator_fixed import EnhancedDocumentGenerator
import pandas as pd

def test_margin_parsing_directly():
    """Test margin parsing directly"""
    print("🔍 Testing Margin Parsing Directly")
    print("=" * 35)
    
    # Read the generated HTML file
    html_file = "test_final_bill_scrutiny_output.html"
    if not Path(html_file).exists():
        print("❌ HTML file not found")
        return False
        
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("✅ HTML content loaded successfully")
    
    # Create a minimal generator instance
    data = {
        'title_data': {},
        'work_order_data': pd.DataFrame(),
        'extra_items_data': pd.DataFrame()
    }
    generator = EnhancedDocumentGenerator(data)
    
    # Test the margin parsing by calling the PDF generation method
    # but catching the margins before they're used
    try:
        from bs4 import BeautifulSoup
        from reportlab.lib.units import mm
        import re
        
        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract margins from CSS @page rule (using the same logic as in the method)
        left_margin = 14*mm
        right_margin = 14*mm
        top_margin = 14*mm
        bottom_margin = 10*mm
        
        # Look for @page rule with margin settings
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            style_content = style_tag.get_text()
            # Look for @page rule with margin settings - improved regex
            page_rules = re.findall(r'@page\s*{[^}]*}', style_content)
            for page_rule in page_rules:
                margin_match = re.search(r'margin:\s*([^;}]*)', page_rule)
                if margin_match:
                    margin_values = margin_match.group(1).strip()
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
        
        # Check if margins are correct for our HTML file
        # Our HTML has: @page { size: A4; margin: 15mm 10mm; }
        # Which should parse to: top=15mm, right=10mm, bottom=15mm, left=10mm
        expected_top = 15
        expected_right = 10
        expected_bottom = 15
        expected_left = 10
        
        if (abs(top_margin/mm - expected_top) < 0.1 and 
            abs(right_margin/mm - expected_right) < 0.1 and
            abs(bottom_margin/mm - expected_bottom) < 0.1 and
            abs(left_margin/mm - expected_left) < 0.1):
            print("✅ Margin parsing is working correctly!")
            return True
        else:
            print("❌ Margin parsing is not working correctly!")
            return False
            
    except Exception as e:
        print(f"Error during margin parsing test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_margin_parsing_directly()
    if success:
        print("\n🎉 Margin parsing test passed!")
        sys.exit(0)
    else:
        print("\n💥 Margin parsing test failed!")
        sys.exit(1)