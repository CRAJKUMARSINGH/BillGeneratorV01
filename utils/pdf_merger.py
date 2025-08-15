import io
from typing import Dict

try:
    from pypdf import PdfReader, PdfWriter  # type: ignore
    PDF_LIB_AVAILABLE = True
except Exception:
    try:
        from PyPDF2 import PdfReader, PdfWriter  # type: ignore
        PDF_LIB_AVAILABLE = True
    except Exception:
        PDF_LIB_AVAILABLE = False

class PDFMerger:
    """Handles PDF merging operations"""
    
    def _select_valid_pdf(self, pdf_files: Dict[str, bytes]) -> bytes:
        """Return the first input that appears to be a valid PDF (starts with %PDF). If none match, return first bytes or empty."""
        for _name, content in pdf_files.items():
            if isinstance(content, (bytes, bytearray)) and content[:4] == b"%PDF":
                return bytes(content)
        # Fallback to first item if available
        if pdf_files:
            return next(iter(pdf_files.values()))
        return b""
    
    def merge_pdfs(self, pdf_files: Dict[str, bytes]) -> bytes:
        """
        Merge multiple PDF files into a single PDF
        
        Args:
            pdf_files: Dictionary of PDF files as bytes
            
        Returns:
            Merged PDF as bytes
        """
        # Preserve insertion order coming from generator
        ordered_items = list(pdf_files.items())

        if not PDF_LIB_AVAILABLE:
            # Return a valid single PDF rather than an invalid concatenation
            return self._select_valid_pdf(dict(ordered_items))

        writer = PdfWriter()
        pages_added = 0
        for name, content in ordered_items:
            try:
                reader = PdfReader(io.BytesIO(content))
                for page in reader.pages:
                    writer.add_page(page)
                    pages_added += 1
            except Exception:
                # Skip invalid PDFs quietly
                continue

        # If no pages could be added, return a valid single PDF input if possible
        if pages_added == 0:
            return self._select_valid_pdf(dict(ordered_items))

        output_stream = io.BytesIO()
        writer.write(output_stream)
        return output_stream.getvalue()
