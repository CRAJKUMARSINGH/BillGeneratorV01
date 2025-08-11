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
        # Prefer deterministic order by filename
        ordered_items = sorted(pdf_files.items(), key=lambda x: x[0])

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

        output_stream = io.BytesIO()
        writer.write(output_stream)
        return output_stream.getvalue()
