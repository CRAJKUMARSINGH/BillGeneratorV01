#!/usr/bin/env python3
"""
Simple verification script to check template data linking
"""

import os

def check_template_variables():
    """Check that templates contain expected Jinja2 variables"""
    
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    
    templates = {
        'first_page.html': [
            'data.header', 'data.bill_items', 'data.extra_items', 
            'data.bill_total', 'data.tender_premium_percent', 'data.bill_premium',
            'data.bill_grand_total', 'data.extra_items_sum', 'data.net_payable'
        ],
        'deviation_statement.html': [
            'data.header', 'data.deviation_items', 'data.deviation_summary',
            'item.serial_no', 'item.description', 'item.unit', 'item.qty_wo',
            'item.rate', 'item.amt_wo', 'item.qty_bill', 'item.amt_bill',
            'item.excess_qty', 'item.excess_amt', 'item.saving_qty', 'item.saving_amt'
        ],
        'extra_items.html': [
            'data.extra_items', 'item.serial_no', 'item.description',
            'item.quantity', 'item.unit', 'item.rate', 'item.amount',
            'data.grand_total', 'data.tender_premium_percent', 'data.tender_premium'
        ],
        'certificate_ii.html': [
            'data.measurement_officer', 'data.measurement_date',
            'data.measurement_book_page', 'data.measurement_book_no',
            'data.officer_name', 'data.officer_designation'
        ],
        'certificate_iii.html': [
            'data.totals.grand_total', 'data.totals.net_payable',
            'data.totals.sd_amount', 'data.totals.it_amount',
            'data.totals.gst_amount', 'data.totals.lc_amount',
            'data.payable_words'
        ],
        'note_sheet.html': [
            'data.agreement_no', 'data.name_of_work', 'data.name_of_firm',
            'data.date_commencement', 'data.date_completion', 'data.actual_completion',
            'data.work_order_amount', 'data.bill_grand_total', 'data.extra_items_sum',
            'data.totals.sd_amount', 'data.totals.it_amount', 'data.totals.gst_amount'
        ]
    }
    
    print("Template Variable Verification")
    print("=" * 40)
    
    all_passed = True
    
    for template_name, expected_vars in templates.items():
        template_path = os.path.join(template_dir, template_name)
        
        if not os.path.exists(template_path):
            print(f"❌ {template_name} - Template file not found")
            all_passed = False
            continue
            
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"\n📄 {template_name}:")
            template_passed = True
            
            for var in expected_vars:
                if var in content:
                    print(f"  ✅ Found: {var}")
                else:
                    print(f"  ❌ Missing: {var}")
                    template_passed = False
                    all_passed = False
                    
            if template_passed:
                print(f"  🎉 All expected variables found in {template_name}")
                
        except Exception as e:
            print(f"  ❌ Error reading {template_name}: {e}")
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 SUCCESS: All templates contain expected variables!")
    else:
        print("❌ FAILURE: Some templates are missing expected variables!")
        
    return all_passed

if __name__ == "__main__":
    check_template_variables()