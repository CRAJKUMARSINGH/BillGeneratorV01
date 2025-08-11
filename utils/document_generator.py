import pandas as pd
from datetime import datetime
from typing import Dict, Any
import io

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
        Convert HTML documents to PDF format
        
        Args:
            documents: Dictionary of HTML documents
            
        Returns:
            Dictionary of PDF documents as bytes
        """
        # Try to use WeasyPrint if available to produce real PDFs that honor @page margins
        pdf_files = {}
        try:
            from weasyprint import HTML  # type: ignore
            weasy_available = True
        except Exception:
            weasy_available = False
        
        for doc_name, html_content in documents.items():
            if weasy_available:
                try:
                    pdf_bytes = HTML(string=html_content, base_url=".").write_pdf()
                except Exception:
                    pdf_bytes = f"PDF content for {doc_name}".encode()
            else:
                pdf_bytes = f"PDF content for {doc_name}".encode()
            pdf_files[f"{doc_name}.pdf"] = pdf_bytes
        
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
                @page {{ size: A4; margin: 10mm; }}
                body {{ font-family: Arial, sans-serif; margin: 0; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
                .subtitle {{ font-size: 14px; margin: 5px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #000; padding: 5px; text-align: left; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">🏛️ Infrastructure Billing System</div>
                <div class="subtitle">First Page Summary</div>
                <div class="subtitle">Date: {current_date}</div>
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
                        <th width="11mm">Item No.</th>
                        <th width="68mm">Item of Work supplies</th>
                        <th width="11.5mm">Unit</th>
                        <th width="16mm">Quantity executed since last certificate</th>
                        <th width="16mm">Quantity executed upto date</th>
                        <th width="15mm">Rate</th>
                        <th width="20.5mm">Amount upto date</th>
                        <th width="16mm">Amount Since previous bill</th>
                        <th width="12.5mm">Remark</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        # Add work order items
        for index, row in self.work_order_data.iterrows():
            # Safely convert numeric values
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            amount = quantity * rate
            
            html_content += f"""
                    <tr>
                        <td>{row.get('Item', '')}</td>
                        <td>{row.get('Description', '')}</td>
                        <td>{row.get('Unit', '')}</td>
                        <td class="amount">{quantity:.2f}</td>
                        <td class="amount">{quantity:.2f}</td>
                        <td class="amount">{rate:.2f}</td>
                        <td class="amount">{amount:.2f}</td>
                        <td class="amount">{amount:.2f}</td>
                        <td></td>
                    </tr>
            """
        
        # Calculate totals
        total_amount = 0
        for _, row in self.work_order_data.iterrows():
            quantity = self._safe_float(row.get('Quantity', 0))
            rate = self._safe_float(row.get('Rate', 0))
            total_amount += quantity * rate
        
        html_content += f"""
                    <tr style="font-weight: bold;">
                        <td colspan="6">TOTAL</td>
                        <td class="amount">{total_amount:.2f}</td>
                        <td class="amount">{total_amount:.2f}</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
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
                @page {{ size: A4 landscape; margin: 10mm; }}
                body {{ font-family: Arial, sans-serif; margin: 0; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
                .subtitle {{ font-size: 14px; margin: 5px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #000; padding: 3px; text-align: left; font-size: 10px; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
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
                matching_rows = self.bill_quantity_data[
                    self.bill_quantity_data['Item'] == wo_row.get('Item')
                ]
                if not matching_rows.empty:
                    bq_row = matching_rows.iloc[0]
            
            wo_qty = self._safe_float(wo_row.get('Quantity', 0))
            wo_rate = self._safe_float(wo_row.get('Rate', 0))
            wo_amount = wo_qty * wo_rate
            
            bq_qty = self._safe_float(bq_row.get('Quantity', 0)) if bq_row is not None else 0
            bq_amount = bq_qty * wo_rate
            
            excess_qty = max(0, bq_qty - wo_qty)
            excess_amt = excess_qty * wo_rate
            saving_qty = max(0, wo_qty - bq_qty)
            saving_amt = saving_qty * wo_rate
            
            html_content += f"""
                    <tr>
                        <td>{wo_row.get('Item', '')}</td>
                        <td>{wo_row.get('Description', '')}</td>
                        <td>{wo_row.get('Unit', '')}</td>
                        <td class="amount">{wo_qty:.2f}</td>
                        <td class="amount">{wo_rate:.2f}</td>
                        <td class="amount">{wo_amount:.2f}</td>
                        <td class="amount">{bq_qty:.2f}</td>
                        <td class="amount">{bq_amount:.2f}</td>
                        <td class="amount">{excess_qty:.2f}</td>
                        <td class="amount">{excess_amt:.2f}</td>
                        <td class="amount">{saving_qty:.2f}</td>
                        <td class="amount">{saving_amt:.2f}</td>
                        <td></td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
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
                @page {{ size: A4; margin: 10mm; }}
                body {{ font-family: Arial, sans-serif; margin: 0; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
                .subtitle {{ font-size: 14px; margin: 5px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #000; padding: 5px; text-align: left; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
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
                        <td>{row.get('Item', '')}</td>
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
                @page {{ size: A4; margin: 10mm; }}
                body {{ font-family: Arial, sans-serif; margin: 0; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
                .subtitle {{ font-size: 14px; margin: 5px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ border: 1px solid #000; padding: 5px; text-align: left; }}
                th {{ background-color: #f0f0f0; font-weight: bold; }}
                .amount {{ text-align: right; }}
            </style>
        </head>
        <body>
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
                amount = row.get('Quantity', 0) * row.get('Rate', 0)
                total_amount += amount
                
                html_content += f"""
                        <tr>
                            <td>{row.get('Item No', '')}</td>
                            <td>{row.get('Description', '')}</td>
                            <td>{row.get('Unit', '')}</td>
                            <td class="amount">{row.get('Quantity', 0):.0f}</td>
                            <td class="amount">{row.get('Rate', 0):.0f}</td>
                            <td class="amount">{amount:.0f}</td>
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
                @page {{ size: A4; margin: 10mm; }}
                body {{ font-family: Arial, sans-serif; margin: 0; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
                .subtitle {{ font-size: 14px; margin: 5px 0; }}
                .content {{ margin: 20px 0; line-height: 1.6; }}
                .signature {{ margin-top: 50px; }}
            </style>
        </head>
        <body>
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
                @page {{ size: A4; margin: 10mm; }}
                body {{ font-family: Arial, sans-serif; margin: 0; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .title {{ font-size: 18px; font-weight: bold; }}
                .subtitle {{ font-size: 14px; margin: 5px 0; }}
                .content {{ margin: 20px 0; line-height: 1.6; }}
                .signature {{ margin-top: 50px; }}
            </style>
        </head>
        <body>
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
        </body>
        </html>
        """
        
        return html_content
