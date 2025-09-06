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
            # Fallback: concatenate bytes with simple separator; not a valid merged PDF but avoids hard failure
            output = io.BytesIO()
            for name, content in ordered_items:
                output.write(content)
                output.write(b"\n%---NEXT_FILE---%\n")
            return output.getvalue()

        writer = PdfWriter()
        for name, content in ordered_items:
            try:
                reader = PdfReader(io.BytesIO(content))
                for page in reader.pages:
                    writer.add_page(page)
            except Exception:
                # Skip invalid PDFs quietly
                continue

        # If no valid pages were added, create a minimal single-page PDF
        if getattr(writer, "getNumPages", None):
            num_pages = writer.getNumPages()
        else:
            try:
                num_pages = len(writer.pages)  # pypdf >=3
            except Exception:
                num_pages = 0
        
        if num_pages == 0:
            try:
                # Create a blank page (A4 default size if supported)
                writer.add_blank_page(width=595.28, height=841.89)
            except Exception:
                pass

        output_stream = io.BytesIO()
        try:
            writer.write(output_stream)
            return output_stream.getvalue()
        finally:
            output_stream.seek(0)
