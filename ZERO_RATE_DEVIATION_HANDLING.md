# Zero Rate Items Handling in Deviation Statement

## Requirement
When the rate of any item or row is blank or equals zero:
- Nothing should be populated in the deviation row except:
  - Item No. (serial_no)

## Implementation

### 1. Template File ([templates/deviation_statement.html](file:///C:/Users/Rajkumar/BillGeneratorV01/templates/deviation_statement.html))

The template now implements conditional logic for zero rate items:

#### Before (Lines 65-79):
```html
{% for item in data.deviation_items %}
<tr>
    <td>{{ item.serial_no or '' }}</td>
    <td>{{ item.description or '' }}</td>
    <td>{{ item.unit or '' }}</td>
    <td>{{ "%.2f" | format(item.qty_wo) if item.qty_wo is defined and item.qty_wo != 0 else '' }}</td>
    <td>{{ "%.2f" | format(item.rate) if item.rate is defined and item.rate != 0 else '' }}</td>
    <td>{{ "%.2f" | format(item.amt_wo) if item.amt_wo is defined and item.amt_wo != 0 else '' }}</td>
    <td>{{ "%.2f" | format(item.qty_bill) if item.qty_bill is defined and item.qty_bill != 0 else '' }}</td>
    <td>{{ "%.2f" | format(item.amt_bill) if item.amt_bill is defined and item.amt_bill != 0 else '' }}</td>
    <td>{{ "%.2f" | format(item.excess_qty) if item.excess_qty is defined and item.excess_qty != 0 else '' }}</td>
    <td>{{ "%.2f" | format(item.excess_amt) if item.excess_amt is defined and item.excess_amt != 0 else '' }}</td>
    <td>{{ "%.2f" | format(item.saving_qty) if item.saving_qty is defined and item.saving_qty != 0 else '' }}</td>
    <td>{{ "%.2f" | format(item.saving_amt) if item.saving_amt is defined and item.saving_amt != 0 else '' }}</td>
    <td>{{ item.remark or '' }}</td>
</tr>
{% endfor %}
```

#### After (Lines 65-79):
```html
{% for item in data.deviation_items %}
<tr>
    <td>{{ item.serial_no or '' }}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ item.description or '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ item.unit or '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ "%.2f" | format(item.qty_wo) if item.qty_wo is defined and item.qty_wo != 0 else '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ "%.2f" | format(item.rate) if item.rate is defined and item.rate != 0 else '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ "%.2f" | format(item.amt_wo) if item.amt_wo is defined and item.amt_wo != 0 else '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ "%.2f" | format(item.qty_bill) if item.qty_bill is defined and item.qty_bill != 0 else '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ "%.2f" | format(item.amt_bill) if item.amt_bill is defined and item.amt_bill != 0 else '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ "%.2f" | format(item.excess_qty) if item.excess_qty is defined and item.excess_qty != 0 else '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ "%.2f" | format(item.excess_amt) if item.excess_amt is defined and item.excess_amt != 0 else '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ "%.2f" | format(item.saving_qty) if item.saving_qty is defined and item.saving_qty != 0 else '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ "%.2f" | format(item.saving_amt) if item.saving_amt is defined and item.saving_amt != 0 else '' }}{% endif %}</td>
    <td>{% if item.rate and item.rate != 0 %}{{ item.remark or '' }}{% endif %}</td>
</tr>
{% endfor %}
```

### 2. Data Preparation ([utils/template_renderer.py](file:///C:/Users/Rajkumar/BillGeneratorV01/utils/template_renderer.py))

The data preparation logic now correctly handles zero rate items in deviation statements:

#### For Zero Rate Items:
- `serial_no`: Preserved (Item No.)
- `description`: Set to empty string `''`
- `unit`: Set to empty string `''`
- `qty_wo`: Set to empty string `''`
- `rate`: Set to empty string `''`
- `amt_wo`: Set to empty string `''`
- `qty_bill`: Set to empty string `''`
- `amt_bill`: Set to empty string `''`
- `excess_qty`: Set to empty string `''`
- `excess_amt`: Set to empty string `''`
- `saving_qty`: Set to empty string `''`
- `saving_amt`: Set to empty string `''`
- `remark`: Set to empty string `''`

#### For Non-Zero Rate Items:
- All fields are populated with their actual values

### 3. Programmatic Generation ([enhanced_document_generator_fixed.py](file:///C:/Users/Rajkumar/BillGeneratorV01/enhanced_document_generator_fixed.py))

The programmatic generation also implements the same logic:

```python
# Apply VBA-like behavior for zero rates
if wo_rate == 0:
    # Only populate Item No. for zero rates
    html_content += f"""
        <tr>
            <td>{self._safe_serial_no(wo_row.get('Item No.', wo_row.get('Item', '')))}</td>
            <td></td>
            <td></td>
            <td class="amount"></td>
            <td class="amount"></td>
            <td class="amount"></td>
            <td class="amount"></td>
            <td class="amount"></td>
            <td class="amount"></td>
            <td class="amount"></td>
            <td class="amount"></td>
            <td class="amount"></td>
        </tr>
    """
else:
    # For non-zero rates, populate all columns
    # ... (full implementation with all values)
```

### 4. Behavior Verification

For zero rate items (rate = 0 or blank):
- ✅ Item No. (serial_no) - POPULATED
- ❌ Description - LEFT BLANK
- ❌ Unit - LEFT BLANK
- ❌ Qty as per Work Order - LEFT BLANK
- ❌ Rate - LEFT BLANK
- ❌ Amt as per Work Order - LEFT BLANK
- ❌ Qty Executed - LEFT BLANK
- ❌ Amt as per Executed - LEFT BLANK
- ❌ Excess Qty - LEFT BLANK
- ❌ Excess Amt - LEFT BLANK
- ❌ Saving Qty - LEFT BLANK
- ❌ Saving Amt - LEFT BLANK
- ❌ Remark - LEFT BLANK

For non-zero rate items:
- ✅ All columns are fully populated with appropriate values

## Conclusion

The implementation fully satisfies the requirement:
> "when rate of any item or row is blank or equals zero >>>>>nothin shuld be populated in deviation* row except >>>>>Item no."

The deviation statement now correctly displays only the Item No. when the rate is zero or blank, while showing all columns for items with non-zero rates.