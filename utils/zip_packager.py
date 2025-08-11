import zipfile
import io
from typing import Dict
from datetime import datetime
from typing import Optional

try:
    from docx import Document  # type: ignore
    from docx.shared import Mm  # type: ignore
    from docx.enum.section import WD_ORIENT  # type: ignore
    DOCX_AVAILABLE = True
except Exception:
    DOCX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup  # type: ignore
    BS4_AVAILABLE = True
except Exception:
    BS4_AVAILABLE = False

class ZipPackager:
    """Handles packaging of documents into ZIP files"""
    
    def create_package(self, documents: Dict[str, str], pdf_files: Dict[str, bytes], merged_pdf: bytes) -> io.BytesIO:
        """
        Create a ZIP package containing all documents in multiple formats
        
        Args:
            documents: Dictionary of HTML documents
            pdf_files: Dictionary of PDF files
            merged_pdf: Merged PDF content
            
        Returns:
            ZIP file as BytesIO buffer
        """
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add HTML documents
            for doc_name, html_content in documents.items():
                filename = f"html/{doc_name.replace(' ', '_').lower()}.html"
                zip_file.writestr(filename, html_content)
            
            # Add individual PDF files
            for pdf_name, pdf_content in pdf_files.items():
                filename = f"pdf/{pdf_name}"
                zip_file.writestr(filename, pdf_content)
            
            # Add merged PDF
            zip_file.writestr("combined/all_documents_combined.pdf", merged_pdf)
            
            # Add Word documents generated from the same HTML
            for doc_name, html_content in documents.items():
                filename = f"word/{doc_name.replace(' ', '_').lower()}.docx"
                docx_bytes = self._html_to_docx_bytes(doc_name, html_content)
                zip_file.writestr(filename, docx_bytes)
        
        zip_buffer.seek(0)
        return zip_buffer

    def _html_to_docx_bytes(self, doc_name: str, html: str) -> bytes:
        """Convert HTML content to a DOCX file in-memory.
        Attempts a faithful representation: text, simple headings, and tables.
        Ensures A4 with 10mm margins; landscape for Deviation Statement.
        """
        # If python-docx is not available, return the HTML bytes as a fallback placeholder
        if not DOCX_AVAILABLE:
            return html.encode("utf-8")

        document = Document()
        # Page setup: A4 with 10 mm margins. Landscape for Deviation Statement
        section = document.sections[0]
        is_landscape = ("deviation" in doc_name.lower())
        if is_landscape:
            section.orientation = WD_ORIENT.LANDSCAPE
            section.page_width = Mm(297)
            section.page_height = Mm(210)
        else:
            section.orientation = WD_ORIENT.PORTRAIT
            section.page_width = Mm(210)
            section.page_height = Mm(297)
        section.top_margin = Mm(10)
        section.bottom_margin = Mm(10)
        section.left_margin = Mm(10)
        section.right_margin = Mm(10)

        if BS4_AVAILABLE:
            soup = BeautifulSoup(html, "html.parser")

            # Title/header if present
            header_div = soup.find(class_="header")
            if header_div:
                for node in header_div.find_all(recursive=False):
                    text = node.get_text(strip=True)
                    if not text:
                        continue
                    if "title" in node.get("class", []):
                        document.add_heading(text, level=1)
                    elif "subtitle" in node.get("class", []):
                        document.add_paragraph(text)

            # Add remaining content: tables and paragraphs
            # Tables
            for table in soup.find_all("table"):
                # Determine number of columns from the first row
                rows = table.find_all("tr")
                if not rows:
                    continue
                first_cells = rows[0].find_all(["th", "td"]) or []
                num_cols = max(1, len(first_cells))
                docx_table = document.add_table(rows=0, cols=num_cols)
                for tr in rows:
                    cells = tr.find_all(["th", "td"]) or []
                    row_cells = docx_table.add_row().cells
                    for idx in range(num_cols):
                        cell_text = cells[idx].get_text(strip=False) if idx < len(cells) else ""
                        # Preserve spacing minimally
                        row_cells[idx].text = " ".join(cell_text.split())

            # Paragraphs outside tables/header
            # Capture top-level paragraphs and divs with text
            for p in soup.find_all(["p", "div"], recursive=True):
                # Skip header and table content already handled
                if p.find_parent("table") or p.get("class") == ["header"]:
                    continue
                text = p.get_text(strip=True)
                if text:
                    document.add_paragraph(text)
        else:
            # Best-effort fallback: strip basic HTML tags
            plain = html
            for tag in ["<br>", "<br/>", "<br />"]:
                plain = plain.replace(tag, "\n")
            # Remove other tags roughly
            import re as _re
            plain = _re.sub(r"<[^>]+>", "", plain)
            for line in [ln.strip() for ln in plain.splitlines() if ln.strip()]:
                document.add_paragraph(line)

        output = io.BytesIO()
        document.save(output)
        return output.getvalue()
