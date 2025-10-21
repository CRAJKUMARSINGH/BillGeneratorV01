
"""
PDF Merger utility for combining multiple PDF documents
"""

import logging
from io import BytesIO

logger = logging.getLogger(__name__)

class PDFMerger:
    """Utility class for merging PDF documents"""
    
    def __init__(self):
        self.available_libraries = self._check_available_libraries()
    
    def _check_available_libraries(self):
        """Check which PDF libraries are available"""
        libraries = {}
        
        try:
            from pypdf import PdfWriter, PdfReader
            libraries['pypdf'] = True
        except ImportError:
            libraries['pypdf'] = False
        
        try:
            from PyPDF2 import PdfWriter, PdfReader
            libraries['PyPDF2'] = True
        except ImportError:
            libraries['PyPDF2'] = False
        
        return libraries
    
    def merge_pdfs(self, pdf_dict):
        """
        Merge multiple PDF files into a single PDF
        
        Args:
            pdf_dict: Dictionary with filename as key and PDF bytes as value
            
        Returns:
            bytes: Merged PDF as bytes
        """
        try:
            if self.available_libraries.get('pypdf', False):
                return self._merge_with_pypdf(pdf_dict)
            elif self.available_libraries.get('PyPDF2', False):
                return self._merge_with_pypdf2(pdf_dict)
            else:
                logger.error("No PDF library available for merging")
                return None
                
        except Exception as e:
            logger.error(f"Error merging PDFs: {str(e)}")
            return None
    
    def _merge_with_pypdf(self, pdf_dict):
        """Merge PDFs using pypdf library"""
        try:
            from pypdf import PdfWriter, PdfReader
            
            writer = PdfWriter()
            
            for filename, pdf_bytes in pdf_dict.items():
                reader = PdfReader(BytesIO(pdf_bytes))
                for page in reader.pages:
                    writer.add_page(page)
            
            output = BytesIO()
            writer.write(output)
            merged_bytes = output.getvalue()
            output.close()
            
            return merged_bytes
            
        except Exception as e:
            logger.error(f"Error with pypdf merging: {str(e)}")
            raise
    
    def _merge_with_pypdf2(self, pdf_dict):
        """Merge PDFs using PyPDF2 library"""
        try:
            from PyPDF2 import PdfWriter, PdfReader
            
            writer = PdfWriter()
            
            for filename, pdf_bytes in pdf_dict.items():
                reader = PdfReader(BytesIO(pdf_bytes))
                for page in reader.pages:
                    writer.add_page(page)
            
            output = BytesIO()
            writer.write(output)
            merged_bytes = output.getvalue()
            output.close()
            
            return merged_bytes
            
        except Exception as e:
            logger.error(f"Error with PyPDF2 merging: {str(e)}")
            raise
    
    def get_pdf_info(self, pdf_bytes):
        """Get information about a PDF file"""
        try:
            if self.available_libraries.get('pypdf', False):
                from pypdf import PdfReader
                reader = PdfReader(BytesIO(pdf_bytes))
                return {
                    'pages': len(reader.pages),
                    'size_bytes': len(pdf_bytes),
                    'title': reader.metadata.get('/Title', 'Unknown') if reader.metadata else 'Unknown'
                }
            elif self.available_libraries.get('PyPDF2', False):
                from PyPDF2 import PdfReader
                reader = PdfReader(BytesIO(pdf_bytes))
                return {
                    'pages': len(reader.pages),
                    'size_bytes': len(pdf_bytes),
                    'title': reader.metadata.get('/Title', 'Unknown') if reader.metadata else 'Unknown'
                }
            else:
                return {
                    'pages': 'Unknown',
                    'size_bytes': len(pdf_bytes),
                    'title': 'Unknown'
                }
        except Exception as e:
            logger.error(f"Error getting PDF info: {str(e)}")
            return {
                'pages': 'Error',
                'size_bytes': len(pdf_bytes),
                'title': 'Error'
            }