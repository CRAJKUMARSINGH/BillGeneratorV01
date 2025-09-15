import pandas as pd
import gc
from datetime import datetime
from typing import Dict, Any
 

class DocumentGenerator:
    """Generates various billing documents from processed Excel data"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.title_data = data.get('title_data', {})
        self.work_order_data = data.get('work_order_data', pd.DataFrame())
        self.bill_quantity_data = data.get('bill_quantity_data', pd.DataFrame())
        self.extra_items_data = data.get('extra_items_data', pd.DataFrame())
    
    def _safe_float(self, value):
        """Safely convert value to float, return 0 if conversion fails"""
        try:
            if pd.isna(value) or value == '' or value is None:
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_serial_no(self, value):
        """Safely convert serial number, return empty string if NaN or None"""
        if pd.isna(value) or value is None or str(value).lower() == 'nan':
            return ''
        return str(value).strip()
    
    def _find_column(self, df, possible_names):
        """Find column by trying multiple possible names"""
        for name in possible_names:
            if name in df.columns:
                return name
        return None
    
    def generate_all_documents(self) -> Dict[str, str]:
        """
        Generate all required documents
        
        Returns:
            Dictionary containing all generated documents in HTML format
        """
        documents = {}
        
        # Generate individual documents
        documents['First Page Summary'] = self._generate_first_page()
        documents['Deviation Statement'] = self._generate_deviation_statement()
        documents['Final Bill Scrutiny Sheet'] = self._generate_final_bill_scrutiny()
        documents['Extra Items Statement'] = self._generate_extra_items_statement()
        documents['Certificate II'] = self._generate_certificate_ii()
        documents['Certificate III'] = self._generate_certificate_iii()
        
        return documents
    
    def create_pdf_documents(self, documents: Dict[str, str]) -> Dict[str, bytes]:
        """
        Convert HTML documents to PDF format with improved margin handling
        
        Args:
            documents: Dictionary of HTML documents
            
        Returns:
            Dictionary of PDF documents as bytes
        """
        pdf_files = {}

        # Prefer WeasyPrint for better CSS @page support, then fall back to xhtml2pdf
        weasy_renderer = None  # type: ignore
        xhtml2pdf_renderer = None  # type: ignore
        
        try:
            from weasyprint import HTML  # type: ignore

            def _render_with_weasy(html_str: str) -> bytes:
                return HTML(string=html_str, base_url=".").write_pdf()

            weasy_renderer = _render_with_weasy
        except Exception:
            pass
            
        try:
            from xhtml2pdf import pisa  # type: ignore
            import io as _io

            def _render_with_xhtml2pdf(html_str: str) -> bytes:
                output = _io.BytesIO()
                pisa.CreatePDF(
                    src=html_str,
                    dest=output,
                    encoding="utf-8",
                    default_css=None,
                    link_callback=None,
                    context_meta={'page_size': 'A4',
                                  'margin_top': '28.35pt',
                                  'margin_right': '28.35pt',
                                  'margin_bottom': '28.35pt',
                                  'margin_left': '28.35pt'}
                )
                return output.getvalue()

            xhtml2pdf_renderer = _render_with_xhtml2pdf
        except Exception:
            pass

        for doc_name, html_content in documents.items():
            pdf_bytes: bytes
            try:
                # Prefer WeasyPrint for better CSS support
                if weasy_renderer is not None:
                    pdf_bytes = weasy_renderer(html_content)
                elif xhtml2pdf_renderer is not None:
                    pdf_bytes = xhtml2pdf_renderer(html_content)
                else:
                    # Last resort fallback
                    pdf_bytes = f"PDF content for {doc_name} - No PDF library available".encode()
            except Exception as e:
                # Try the alternate engine if available
                try:
                    if xhtml2pdf_renderer is not None:
                        pdf_bytes = xhtml2pdf_renderer(html_content)
                    else:
                        pdf_bytes = f"PDF generation failed for {doc_name}: {str(e)}".encode()
                except Exception:
                    pdf_bytes = f"PDF generation failed for {doc_name}: {str(e)}".encode()
                    
            pdf_files[f"{doc_name}.pdf"] = pdf_bytes
        
        # Memory cleanup
        gc.collect()
        return pdf_files
    
    def _generate_first_page(self) -> str:
        """Generate First Page Summary document"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>First Page Summary</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 10pt; 
                }}
                .page {{ 
                    margin: 0;
                    padding: 0;
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 6px 0; table-layout: fixed; }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ border: 1px solid #000; padding: 4px; text-align: left; word-wrap: break-word; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="page">
            <div class="header">
                <div class="title">🏛️ Infrastructure Billing System</div>
                <div class="subtitle">First Page Summary</div>
                <div class="subtitle">Date: {current_date}</div>
                <div style="font-size: 8pt; color: #666; margin-top: 5px; font-style: italic;">Enhanced document formatting powered by Warp AI Terminal</div>
            </div>
            
            <h3>Project Information</h3>
            <table>
                <tr><td><strong>Project Name:</strong></td><td>{self.title_data.get('Project Name', 'N/A')}</td></tr>
                <tr><td><strong>Contract No:</strong></td><td>{self.title_data.get('Contract No', 'N/A')}</td></tr>
                <tr><td><strong>Work Order No:</strong></td><td>{self.title_data.get('Work Order No', 'N/A')}</td></tr>
            </table>
            
            <h3>Work Items Summary</h3>
            <table>
                <thead>
                    <tr>
                        <th width="11.7mm">Unit</th>
                        <th width="16mm">Quantity executed (or supplied) since last certificate</th>
                        <th width="16mm">Quantity executed (or supplied) upto date as per MB</th>
                        <th width="11.1mm">Item No.</th>
                        <th width="74.2mm">Item of Work supplies (Grouped under "sub-head" and "sub work" of estimate)</th>
                        <th width="15.3mm">Rate</th>
                        <th width="22.7mm">Amount upto date</th>
                        <th width="17.6mm">Amount Since previous bill (Total for each sub-head)</th>
                        <th width="13.9mm">Remark</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add work order items
        for index, row in self.work_order_data.iterrows():
            # Safely convert numeric values - handle both old and new column names
            quantity_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            quantity_upto = self._safe_float(row.get('Quantity Upto', quantity_since))
            rate = self._safe_float(row.get('Rate', 0))
            amount_since = self._safe_float(row.get('Amount Since', quantity_since * rate))
            amount_upto = self._safe_float(row.get('Amount Upto', amount_since))
            
            # Format values conditionally
            qty_since_display = f"{quantity_since:.2f}" if quantity_since > 0 else ""
            qty_upto_display = f"{quantity_upto:.2f}" if quantity_upto > 0 else ""
            rate_display = f"{rate:.2f}" if rate > 0 else ""
            amt_upto_display = f"{amount_upto:.2f}" if amount_upto > 0 else ""
            amt_since_display = f"{amount_since:.2f}" if amount_since > 0 else ""
            
            html_content += f"""
                    <tr>
                        <td>{row.get('Unit', '')}</td>
                        <td class="amount">{qty_since_display}</td>
                        <td class="amount">{qty_upto_display}</td>
                        <td>{self._safe_serial_no(row.get('Item No.', row.get('Item', '')))}</td>
                        <td>{row.get('Description', '')}</td>
                        <td class="amount">{rate_display}</td>
                        <td class="amount">{amt_upto_display}</td>
                        <td class="amount">{amt_since_display}</td>
                        <td>{row.get('Remark', '')}</td>
                    </tr>
            """
        
        # Calculate totals
        total_amount = 0
        for _, row in self.work_order_data.iterrows():
            quantity_since = self._safe_float(row.get('Quantity Since', row.get('Quantity', 0)))
            rate = self._safe_float(row.get('Rate', 0))
            total_amount += quantity_since * rate
        
        html_content += f"""
                    <tr style="font-weight: bold;">
                        <td colspan="6">TOTAL</td>
                        <td class="amount">{total_amount:.2f}</td>
                        <td class="amount">{total_amount:.2f}</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_deviation_statement(self) -> str:
        """Generate Deviation Statement document"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Deviation Statement</title>
            <style>
                @page {{ 
                    size: A4 landscape; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 9pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 14pt; font-weight: bold; }}
                .subtitle {{ font-size: 10pt; margin: 3px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 4px 0; table-layout: fixed; }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ border: 1px solid #000; padding: 3px; text-align: left; word-wrap: break-word; font-size: 8.5pt; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="page">
            <div class="header">
                <div class="title">🏛️ Infrastructure Billing System</div>
                <div class="subtitle">Deviation Statement</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th width="6mm">ITEM No.</th>
                        <th width="95mm">Description</th>
                        <th width="10mm">Unit</th>
                        <th width="10mm">Qty as per Work Order</th>
                        <th width="12mm">Rate</th>
                        <th width="12mm">Amt as per Work Order Rs.</th>
                        <th width="12mm">Qty Executed</th>
                        <th width="12mm">Amt as per Executed Rs.</th>
                        <th width="12mm">Excess Qty</th>
                        <th width="12mm">Excess Amt Rs.</th>
                        <th width="12mm">Saving Qty</th>
                        <th width="12mm">Saving Amt Rs.</th>
                        <th width="40mm">REMARKS/ REASON.</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Compare work order with bill quantity data
        for index, wo_row in self.work_order_data.iterrows():
            # Find corresponding bill quantity row
            bq_row = None
            if not self.bill_quantity_data.empty:
                wo_item = wo_row.get('Item No.', wo_row.get('Item', ''))
                bq_item_col = 'Item No.' if 'Item No.' in self.bill_quantity_data.columns else 'Item'
                matching_rows = self.bill_quantity_data[
                    self.bill_quantity_data[bq_item_col] == wo_item
                ]
                if not matching_rows.empty:
                    bq_row = matching_rows.iloc[0]
            
            wo_qty = self._safe_float(wo_row.get('Quantity Since', wo_row.get('Quantity', 0)))
            wo_rate = self._safe_float(wo_row.get('Rate', 0))
            wo_amount = wo_qty * wo_rate
            
            bq_qty = self._safe_float(bq_row.get('Quantity', 0)) if bq_row is not None else 0
            bq_amount = bq_qty * wo_rate
            
            excess_qty = max(0, bq_qty - wo_qty)
            excess_amt = excess_qty * wo_rate
            saving_qty = max(0, wo_qty - bq_qty)
            saving_amt = saving_qty * wo_rate
            
            # Format deviation values conditionally
            wo_qty_display = f"{wo_qty:.2f}" if wo_qty > 0 else ""
            wo_rate_display = f"{wo_rate:.2f}" if wo_rate > 0 else ""
            wo_amount_display = f"{wo_amount:.2f}" if wo_amount > 0 else ""
            bq_qty_display = f"{bq_qty:.2f}" if bq_qty > 0 else ""
            bq_amount_display = f"{bq_amount:.2f}" if bq_amount > 0 else ""
            excess_qty_display = f"{excess_qty:.2f}" if excess_qty > 0 else ""
            excess_amt_display = f"{excess_amt:.2f}" if excess_amt > 0 else ""
            saving_qty_display = f"{saving_qty:.2f}" if saving_qty > 0 else ""
            saving_amt_display = f"{saving_amt:.2f}" if saving_amt > 0 else ""
            
            html_content += f"""
                    <tr>
                        <td>{self._safe_serial_no(wo_row.get('Item No.', wo_row.get('Item', '')))}</td>
                        <td>{wo_row.get('Description', '')}</td>
                        <td>{wo_row.get('Unit', '')}</td>
                        <td class="amount">{wo_qty_display}</td>
                        <td class="amount">{wo_rate_display}</td>
                        <td class="amount">{wo_amount_display}</td>
                        <td class="amount">{bq_qty_display}</td>
                        <td class="amount">{bq_amount_display}</td>
                        <td class="amount">{excess_qty_display}</td>
                        <td class="amount">{excess_amt_display}</td>
                        <td class="amount">{saving_qty_display}</td>
                        <td class="amount">{saving_amt_display}</td>
                        <td></td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_final_bill_scrutiny(self) -> str:
        """Generate Final Bill Scrutiny Sheet"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Final Bill Scrutiny Sheet</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 10pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 6px 0; table-layout: fixed; }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ border: 1px solid #000; padding: 4px; text-align: left; word-wrap: break-word; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="page">
            <div class="header">
                <div class="title">🏛️ Infrastructure Billing System</div>
                <div class="subtitle">Final Bill Scrutiny Sheet</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <h3>Bill Summary</h3>
            <table>
                <thead>
                    <tr>
                        <th>Item No.</th>
                        <th>Description</th>
                        <th>Unit</th>
                        <th>Quantity</th>
                        <th>Rate</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        total_amount = 0
        for index, row in self.bill_quantity_data.iterrows():
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            total_amount += amount
            
            html_content += f"""
                    <tr>
                        <td>{self._safe_serial_no(row.get('Item No.', row.get('Item', '')))}</td>
                        <td>{row.get('Description', '')}</td>
                        <td>{row.get('Unit', '')}</td>
                        <td class="amount">{quantity:.2f}</td>
                        <td class="amount">{rate:.2f}</td>
                        <td class="amount">{amount:.2f}</td>
                    </tr>
            """
        
        html_content += f"""
                    <tr style="font-weight: bold;">
                        <td colspan="5">TOTAL</td>
                        <td class="amount">{total_amount:.0f}</td>
                    </tr>
                </tbody>
            </table>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_extra_items_statement(self) -> str:
        """Generate Extra Items Statement"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Extra Items Statement</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 10pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 6px 0; table-layout: fixed; }}
                thead {{ display: table-header-group; }}
                tr, img {{ break-inside: avoid; }}
                th, td {{ border: 1px solid #000; padding: 4px; text-align: left; word-wrap: break-word; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="page">
            <div class="header">
                <div class="title">🏛️ Infrastructure Billing System</div>
                <div class="subtitle">Extra Items Statement</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
        """
        
        if not self.extra_items_data.empty:
            html_content += """
            <h3>Extra Items</h3>
            <table>
                <thead>
                    <tr>
                        <th>Item No.</th>
                        <th>Description</th>
                        <th>Unit</th>
                        <th>Quantity</th>
                        <th>Rate</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            total_amount = 0
            for index, row in self.extra_items_data.iterrows():
                quantity = self._safe_float(row.get('Quantity', 0))
                rate = self._safe_float(row.get('Rate', 0))
                amount = quantity * rate
                total_amount += amount
                
                html_content += f"""
                        <tr>
                            <td>{self._safe_serial_no(row.get('Item No.', row.get('Item No', row.get('Item', ''))))}</td>
                            <td>{row.get('Description', '')}</td>
                            <td>{row.get('Unit', '')}</td>
                            <td class="amount">{quantity:.2f}</td>
                            <td class="amount">{rate:.2f}</td>
                            <td class="amount">{amount:.2f}</td>
                        </tr>
                """
            
            html_content += f"""
                        <tr style="font-weight: bold;">
                            <td colspan="5">TOTAL</td>
                            <td class="amount">{total_amount:.0f}</td>
                        </tr>
                    </tbody>
                </table>
            """
        else:
            html_content += "<p>No extra items found in the provided data.</p>"
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_ii(self) -> str:
        """Generate Certificate II"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Certificate II</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 11pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                .content {{ margin: 10px 0; line-height: 1.5; }}
                .signature {{ margin-top: 40px; }}
            </style>
        </head>
        <body>
            <div class="page">
            <div class="header">
                <div class="title">🏛️ Infrastructure Billing System</div>
                <div class="subtitle">Certificate II</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <div class="content">
                <p>This is to certify that the work described in the bill has been executed according to the specifications and is complete in all respects.</p>
                
                <p><strong>Project Details:</strong></p>
                <ul>
                    <li>Project Name: {self.title_data.get('Project Name', 'N/A')}</li>
                    <li>Contract No: {self.title_data.get('Contract No', 'N/A')}</li>
                    <li>Work Order No: {self.title_data.get('Work Order No', 'N/A')}</li>
                </ul>
                
                <p>The work has been executed in accordance with the contract terms and conditions.</p>
            </div>
            
            <div class="signature">
                <p>_________________________</p>
                <p>Engineer-in-Charge</p>
                <p>Date: {current_date}</p>
            </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def _generate_certificate_iii(self) -> str:
        """Generate Certificate III"""
        current_date = datetime.now().strftime('%d/%m/%Y')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Certificate III</title>
            <style>
                @page {{ 
                    size: A4; 
                    margin: 10mm 10mm 10mm 10mm;
                    margin-top: 10mm;
                    margin-right: 10mm;
                    margin-bottom: 10mm;
                    margin-left: 10mm;
                }}
                * {{ box-sizing: border-box; }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 10mm;
                    font-size: 11pt; 
                }}
                .page {{ }}
                .header {{ text-align: center; margin-bottom: 8px; }}
                .title {{ font-size: 16pt; font-weight: bold; }}
                .subtitle {{ font-size: 11pt; margin: 3px 0; }}
                .content {{ margin: 10px 0; line-height: 1.5; }}
                .signature {{ margin-top: 40px; }}
            </style>
        </head>
        <body>
            <div class="page">
            <div class="header">
                <div class="title">🏛️ Infrastructure Billing System</div>
                <div class="subtitle">Certificate III</div>
                <div class="subtitle">Date: {current_date}</div>
            </div>
            
            <div class="content">
                <p>This is to certify that the rates charged in the bill are in accordance with the contract and approved rate schedule.</p>
                
                <p><strong>Project Details:</strong></p>
                <ul>
                    <li>Project Name: {self.title_data.get('Project Name', 'N/A')}</li>
                    <li>Contract No: {self.title_data.get('Contract No', 'N/A')}</li>
                    <li>Work Order No: {self.title_data.get('Work Order No', 'N/A')}</li>
                </ul>
                
                <p>All rates and calculations have been verified and are correct.</p>
            </div>
            
            <div class="signature">
                <p>_________________________</p>
                <p>Accounts Officer</p>
                <p>Date: {current_date}</p>
            </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
