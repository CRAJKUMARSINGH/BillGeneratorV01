# Template Data Linking - Comprehensive Guide

## Overview
This document provides a comprehensive guide on how data is linked to each template in the BillGeneratorV01 system. All templates use Jinja2 templating engine for dynamic data insertion.

## 1. First Page Template (first_page.html)

### Data Structure
The first page template expects data in the following structure:
```json
{
  "data": {
    "header": [
      ["key: value", "key: value", "key: value"],
      ["key: value", "key: value", "key: value"]
    ],
    "bill_items": [
      {
        "unit": "string",
        "quantity_since": "number",
        "quantity_upto": "number",
        "serial_no": "string",
        "description": "string",
        "rate": "number",
        "amount_upto": "number",
        "amount_since": "number",
        "remark": "string"
      }
    ],
    "extra_items": [
      {
        "unit": "string",
        "quantity_since": "number",
        "quantity_upto": "number",
        "serial_no": "string",
        "description": "string",
        "rate": "number",
        "amount_upto": "number",
        "amount_since": "number",
        "remark": "string"
      }
    ],
    "bill_total": "number",
    "tender_premium_percent": "number",
    "bill_premium": "number",
    "bill_grand_total": "number",
    "extra_items_base": "number",
    "extra_premium": "number",
    "extra_items_sum": "number",
    "last_bill_amount": "number",
    "net_payable": "number"
  }
}
```

### Key Template Variables
- `{{ data.header }}` - Project information header (2D array)
- `{{ data.bill_items }}` - Main work order items (array)
- `{{ item.unit }}` - Unit of measurement for each item
- `{{ item.quantity_since }}` - Quantity since last certificate
- `{{ item.quantity_upto }}` - Quantity up to date
- `{{ item.serial_no }}` - Serial number of item
- `{{ item.description }}` - Description of item
- `{{ item.rate }}` - Rate per unit
- `{{ item.amount_upto }}` - Amount up to date
- `{{ item.amount_since }}` - Amount since previous bill
- `{{ item.remark }}` - Remarks for item
- `{{ data.extra_items }}` - Extra items (array)
- `{{ data.bill_total }}` - Main items total amount
- `{{ data.tender_premium_percent }}` - Tender premium percentage
- `{{ data.bill_premium }}` - Tender premium amount for main items
- `{{ data.bill_grand_total }}` - Grand total for main items
- `{{ data.extra_items_base }}` - Base amount for extra items
- `{{ data.extra_premium }}` - Tender premium for extra items
- `{{ data.extra_items_sum }}` - Grand total for extra items
- `{{ data.last_bill_amount }}` - Previous bill amount
- `{{ data.net_payable }}` - Net payable amount

## 2. Deviation Statement Template (deviation_statement.html)

### Data Structure
```json
{
  "data": {
    "header": [
      ["", "", "", "", "agreement_no"],
      ["", "name_of_work"]
    ],
    "deviation_items": [
      {
        "serial_no": "string",
        "description": "string",
        "unit": "string",
        "qty_wo": "number",
        "rate": "number",
        "amt_wo": "number",
        "qty_bill": "number",
        "amt_bill": "number",
        "excess_qty": "number",
        "excess_amt": "number",
        "saving_qty": "number",
        "saving_amt": "number",
        "remark": "string"
      }
    ],
    "deviation_summary": {
      "work_order_total": "number",
      "executed_total": "number",
      "overall_excess": "number",
      "overall_saving": "number",
      "tender_premium_f": "number",
      "tender_premium_h": "number",
      "tender_premium_j": "number",
      "tender_premium_l": "number",
      "grand_total_f": "number",
      "grand_total_h": "number",
      "grand_total_j": "number",
      "grand_total_l": "number",
      "net_difference": "number"
    },
    "tender_premium_percent": "number"
  }
}
```

### Key Template Variables
- `{{ data.header }}` - Header information
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

### Data Structure
```json
{
  "data": {
    "extra_items": [
      {
        "serial_no": "string",
        "reference": "string",
        "description": "string",
        "quantity": "number",
        "unit": "string",
        "rate": "number",
        "amount": "number",
        "remark": "string"
      }
    ],
    "grand_total": "number",
    "tender_premium_percent": "number",
    "tender_premium": "number",
    "total_executed": "number"
  }
}
```

### Key Template Variables
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

### Data Structure
```json
{
  "data": {
    "measurement_officer": "string",
    "measurement_date": "string",
    "measurement_book_page": "string",
    "measurement_book_no": "string",
    "officer_name": "string",
    "officer_designation": "string",
    "authorising_officer_name": "string",
    "authorising_officer_designation": "string"
  }
}
```

### Key Template Variables
- `{{ data.measurement_officer }}` - Name of officer who made measurements
- `{{ data.measurement_date }}` - Date of measurement
- `{{ data.measurement_book_page }}` - Page number in measurement book
- `{{ data.measurement_book_no }}` - Measurement book number
- `{{ data.officer_name }}` - Name of officer preparing the bill
- `{{ data.officer_designation }}` - Designation of officer preparing the bill
- `{{ data.authorising_officer_name }}` - Name of officer authorising payment
- `{{ data.authorising_officer_designation }}` - Designation of officer authorising payment

## 5. Certificate III Template (certificate_iii.html)

### Data Structure
```json
{
  "data": {
    "totals": {
      "grand_total": "number",
      "net_payable": "number",
      "sd_amount": "number",
      "it_amount": "number",
      "gst_amount": "number",
      "lc_amount": "number",
      "total_deductions": "number"
    },
    "payable_words": "string"
  }
}
```

### Key Template Variables
- `{{ data.totals.grand_total }}` - Grand total amount
- `{{ data.totals.net_payable }}` - Net payable amount
- `{{ data.totals.sd_amount }}` - Security deposit amount (10%)
- `{{ data.totals.it_amount }}` - Income tax amount (2%)
- `{{ data.totals.gst_amount }}` - GST amount (2%)
- `{{ data.totals.lc_amount }}` - Labour cess amount (1%)
- `{{ data.totals.total_deductions }}` - Total deductions
- `{{ data.payable_words }}` - Amount in words

## 6. Note Sheet Template (note_sheet.html)

### Data Structure
```json
{
  "data": {
    "agreement_no": "string",
    "name_of_work": "string",
    "name_of_firm": "string",
    "date_commencement": "string",
    "date_completion": "string",
    "actual_completion": "string",
    "work_order_amount": "number",
    "bill_grand_total": "number",
    "extra_items_sum": "number",
    "totals": {
      "sd_amount": "number",
      "it_amount": "number",
      "gst_amount": "number",
      "lc_amount": "number",
      "liquidated_damages": "number",
      "net_payable": "number"
    }
  }
}
```

### Key Template Variables
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

## Data Flow Process

1. **Input Processing**: Excel files are processed by `excel_processor.py` and converted to pandas DataFrames
2. **Data Preparation**: `enhanced_document_generator_fixed.py` processes the data and calculates all necessary totals and values
3. **Template Data Formatting**: `utils/template_renderer.py` formats the data specifically for each template's requirements
4. **Template Rendering**: Jinja2 engine renders each template with its corresponding data
5. **Output Generation**: HTML documents are generated and can be converted to PDF if needed

## Key Features

- **Dynamic Data Binding**: All templates use Jinja2 templating for dynamic data insertion
- **Conditional Logic**: Templates include conditional rendering based on data values
- **Formatting Consistency**: All templates follow consistent formatting and styling
- **Error Handling**: Templates gracefully handle missing or empty data
- **Extensibility**: Template structure allows for easy addition of new fields

This comprehensive linking ensures that all templates receive the correct data and render properly with accurate information.