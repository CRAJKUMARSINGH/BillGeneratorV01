import zipfile
import io
from typing import Dict
from datetime import datetime

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
            
            # Add Word document placeholders (would be generated from HTML in real implementation)
            for doc_name in documents.keys():
                filename = f"word/{doc_name.replace(' ', '_').lower()}.docx"
                word_content = f"Word document for {doc_name}".encode()
                zip_file.writestr(filename, word_content)
        
        zip_buffer.seek(0)
        return zip_buffer
