# Template Data Mapping Documentation

## Overview
This document details how data is linked to each template in the BillGeneratorV01 system. Each template uses Jinja2 templating to dynamically insert data values.

## 1. First Page Template (first_page.html)

### Data Structure Expected:
```json
{
  "data": {
    "header": [
      ["Project Name: XYZ Project", "Contract No: 123/2024", "Work Order No: WO-001"],
      ["Contractor Name: ABC Company", "Bill Number: First", "Bill Type: Final"]
    ],
    "bill_items": [
      {
        "unit": "Meter",
        "quantity_since": "100.00",
        "quantity_upto": "100.00",
        "serial_no": "1",
        "description": "Electrical Wiring",
        "rate": "50.00",
        "amount_upto": "5000.00",
        "amount_since": "5000.00",
        "remark": "Completed"
      }
    ],
    "extra_items": [
      {
        "unit": "Lot",
        "quantity_since": "1.00",
        "quantity_upto": "1.00",
        "serial_no": "E1",
        "description": "Emergency Repairs",
        "rate": "5000.00",
        "amount_upto": "5000.00",
        "amount_since": "5000.00",
        "remark": "Urgent repair work"
      }
    ],
    "bill_total": "5000.00",
    "tender_premium_percent": 10.0,
    "bill_premium": "500.00",
    "bill_grand_total": "5500.00",
    "extra_items_base": "5000.00",
    "extra_premium": "500.00",
    "extra_items_sum": "5500.00",
    "last_bill_amount": "0.00",
    "net_payable": "11000.00"
  }
}
```

### Template Variables Mapped:
- `{{ data.header }}` - Project information header
- `{{ data.bill_items }}` - Main work order items
- `{{ data.extra_items }}` - Extra items (if any)
- `{{ data.bill_total }}` - Main items total amount
- `{{ data.tender_premium_percent }}` - Tender premium percentage
- `{{ data.bill_premium }}` - Tender premium amount for main items
- `{{ data.bill_grand_total }}` - Grand total for main items
- `{{ data.extra_items_base }}` - Base amount for extra items
- `{{ data.extra_premium }}` - Tender premium for extra items
- `{{ data.extra_items_sum }}` - Grand total for extra items
- `{{ data.last_bill_amount }}` - Previous bill amount (for deductions)
- `{{ data.net_payable }}` - Net payable amount

## 2. Deviation Statement Template (deviation_statement.html)

### Data Structure Expected:
```json
{
  "data": {
    "header": [
      ["", "", "", "", "123/2024"],
      ["", "XYZ Construction Project"]
    ],
    "deviation_items": [
      {
        "serial_no": "1",
        "description": "Electrical Wiring",
        "unit": "Meter",
        "qty_wo": "100.00",
        "rate": "50.00",
        "amt_wo": "5000.00",
        "qty_bill": "110.00",
        "amt_bill": "5500.00",
        "excess_qty": "10.00",
        "excess_amt": "500.00",
        "saving_qty": "",
        "saving_amt": "",
        "remark": "Additional wiring required"
      }
    ],
    "deviation_summary": {
      "work_order_total": "5000.00",
      "executed_total": "5500.00",
      "overall_excess": "500.00",
      "overall_saving": "0.00",
      "tender_premium_f": "500.00",
      "tender_premium_h": "550.00",
      "tender_premium_j": "50.00",
      "tender_premium_l": "0.00",
      "grand_total_f": "5500.00",
      "grand_total_h": "6050.00",
      "grand_total_j": "550.00",
      "grand_total_l": "0.00",
      "net_difference": "500.00"
    },
    "tender_premium_percent": 0.10
  }
}
```

### Template Variables Mapped:
- `{{ data.header }}` - Header information with agreement number and work name
- `{{ data.deviation_items }}` - Deviation calculation items
- `{{ item.serial_no }}` - Item serial number
- `{{ item.description }}` - Item description
- `{{ item.unit }}` - Unit of measurement
- `{{ item.qty_wo }}` - Quantity as per work order
- `{{ item.rate }}` - Rate per unit
- `{{ item.amt_wo }}` - Amount as per work order
- `{{ item.qty_bill }}` - Quantity executed/billed
- `{{ item.amt_bill }}` - Amount executed/billed
- `{{ item.excess_qty }}` - Excess quantity
- `{{ item.excess_amt }}` - Excess amount
- `{{ item.saving_qty }}` - Saving quantity
- `{{ item.saving_amt }}` - Saving amount
- `{{ item.remark }}` - Remarks
- `{{ data.deviation_summary.work_order_total }}` - Total work order amount
- `{{ data.deviation_summary.executed_total }}` - Total executed amount
- `{{ data.deviation_summary.overall_excess }}` - Overall excess amount
- `{{ data.deviation_summary.overall_saving }}` - Overall saving amount
- `{{ data.tender_premium_percent }}` - Tender premium percentage

## 3. Extra Items Template (extra_items.html)

### Data Structure Expected:
```json
{
  "data": {
    "extra_items": [
      {
        "serial_no": "E1",
        "reference": "Ref-001",
        "description": "Emergency Repairs",
        "quantity": 1,
        "unit": "Lot",
        "rate": 5000,
        "amount": 5000,
        "remark": "Urgent repair work"
      }
    ],
    "grand_total": 5000,
    "tender_premium_percent": 0.10,
    "tender_premium": 500,
    "total_executed": 5500
  }
}
```

### Template Variables Mapped:
- `{{ data.extra_items }}` - Extra items list
- `{{ item.serial_no }}` - Serial number of extra item
- `{{ item.reference }}` - Reference BSR number
- `{{ item.description }}` - Description of extra item
- `{{ item.quantity }}` - Quantity of extra item
- `{{ item.unit }}` - Unit of extra item
- `{{ item.rate }}` - Rate of extra item
- `{{ item.amount }}` - Amount of extra item
- `{{ item.remark }}` - Remarks for extra item
- `{{ data.grand_total }}` - Grand total of extra items
- `{{ data.tender_premium_percent }}` - Tender premium percentage
- `{{ data.tender_premium }}` - Tender premium amount
- `{{ data.total_executed }}` - Total amount of extra items executed

## 4. Certificate II Template (certificate_ii.html)

### Data Structure Expected:
```json
{
  "data": {
    "measurement_officer": "Shri Rajesh Kumar",
    "measurement_date": "15/10/2025",
    "measurement_book_page": "45",
    "measurement_book_no": "MB-2025-001",
    "officer_name": "Shri Arun Sharma",
    "officer_designation": "Assistant Executive Engineer",
    "authorising_officer_name": "Shri Deepak Verma",
    "authorising_officer_designation": "Executive Engineer"
  }
}
```

### Template Variables Mapped:
- `{{ data.measurement_officer }}` - Name of officer who made measurements
- `{{ data.measurement_date }}` - Date of measurement
- `{{ data.measurement_book_page }}` - Page number in measurement book
- `{{ data.measurement_book_no }}` - Measurement book number
- `{{ data.officer_name }}` - Name of officer preparing the bill
- `{{ data.officer_designation }}` - Designation of officer preparing the bill
- `{{ data.authorising_officer_name }}` - Name of officer authorising payment
- `{{ data.authorising_officer_designation }}` - Designation of officer authorising payment

## 5. Certificate III Template (certificate_iii.html)

### Data Structure Expected:
```json
{
  "data": {
    "totals": {
      "grand_total": "5500",
      "net_payable": "6050",
      "sd_amount": "605",
      "it_amount": "121",
      "gst_amount": "121",
      "lc_amount": "60",
      "total_deductions": "907"
    },
    "payable_words": "Six Thousand Fifty Only"
  }
}
```

### Template Variables Mapped:
- `{{ data.totals.grand_total }}` - Grand total amount
- `{{ data.totals.net_payable }}` - Net payable amount
- `{{ data.totals.sd_amount }}` - Security deposit amount (10%)
- `{{ data.totals.it_amount }}` - Income tax amount (2%)
- `{{ data.totals.gst_amount }}` - GST amount (2%)
- `{{ data.totals.lc_amount }}` - Labour cess amount (1%)
- `{{ data.totals.total_deductions }}` - Total deductions
- `{{ data.payable_words }}` - Amount in words
- `{{ data.totals.grand_total | round(0) | int }}` - Rounded grand total
- `{{ data.totals.net_payable | round(0) | int }}` - Rounded net payable
- `{{ data.totals.sd_amount | round(0) | int }}` - Rounded SD amount
- `{{ data.totals.it_amount | round(0) | int }}` - Rounded IT amount
- `{{ data.totals.gst_amount | round(0) | int }}` - Rounded GST amount
- `{{ data.totals.lc_amount | round(0) | int }}` - Rounded LC amount
- `{{ data.totals.total_deductions | round(0) | int }}` - Rounded total deductions

## 6. Note Sheet Template (note_sheet.html)

### Data Structure Expected:
```json
{
  "data": {
    "agreement_no": "123/2024",
    "name_of_work": "XYZ Construction Project",
    "name_of_firm": "ABC Construction Company",
    "date_commencement": "01/01/2025",
    "date_completion": "31/12/2025",
    "actual_completion": "30/11/2025",
    "work_order_amount": "100000",
    "bill_grand_total": "110000",
    "extra_items_sum": "5500",
    "totals": {
      "sd_amount": "11000",
      "it_amount": "2200",
      "gst_amount": "2200",
      "lc_amount": "1100",
      "liquidated_damages": "0",
      "net_payable": "95700"
    }
  }
}
```

### Template Variables Mapped:
- `{{ data.agreement_no }}` - Agreement number
- `{{ data.name_of_work }}` - Name of work/project
- `{{ data.name_of_firm }}` - Name of contractor/firm
- `{{ data.date_commencement }}` - Date of commencement
- `{{ data.date_completion }}` - Date of completion
- `{{ data.actual_completion }}` - Actual completion date
- `{{ data.work_order_amount }}` - Work order amount
- `{{ data.bill_grand_total }}` - Bill grand total
- `{{ data.extra_items_sum }}` - Extra items sum
- `{{ data.totals.sd_amount }}` - Security deposit amount
- `{{ data.totals.it_amount }}` - Income tax amount
- `{{ data.totals.gst_amount }}` - GST amount
- `{{ data.totals.lc_amount }}` - Labour cess amount
- `{{ data.totals.liquidated_damages }}` - Liquidated damages
- `{{ data.totals.net_payable }}` - Net payable amount
- Conditional logic for delay handling
- Conditional logic for extra items
- Dynamic calculation of progress percentage

## Data Flow Summary

1. **Data Source**: Excel input files are processed by `excel_processor.py` and converted to pandas DataFrames
2. **Data Processing**: `enhanced_document_generator_fixed.py` processes the data and calculates totals
3. **Template Preparation**: `utils/template_renderer.py` prepares data in the format expected by each template
4. **Template Rendering**: Jinja2 renders the templates with the prepared data
5. **Output Generation**: HTML documents are generated and can be converted to PDF

Each template expects a specific data structure, and the TemplateRenderer class ensures that data is formatted correctly for each template's requirements.