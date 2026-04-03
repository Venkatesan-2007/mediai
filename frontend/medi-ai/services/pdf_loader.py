"""
PDF Loader Service
Extracts text from all PDFs in a given folder
"""
import os
import pdfplumber
from pathlib import Path
from typing import List, Dict


class PDFLoader:
    def __init__(self, folder_path: str):
        self.folder_path = folder_path
        self.documents = []
        
    def load_pdfs(self) -> List[Dict[str, str]]:
        """
        Load and extract text from all PDFs in the folder
        Returns: List of dicts with 'filename' and 'text' keys
        """
        folder = Path(self.folder_path)
        
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {self.folder_path}")
        
        pdf_files = list(folder.glob("*.pdf"))
        
        if not pdf_files:
            raise ValueError(f"No PDF files found in {self.folder_path}")
        
        documents = []
        
        for pdf_file in pdf_files:
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    
                    if text.strip():
                        documents.append({
                            "filename": pdf_file.name,
                            "text": text.strip()
                        })
                        print(f"✓ Loaded: {pdf_file.name} ({len(text)} chars)")
            except Exception as e:
                print(f"✗ Error loading {pdf_file.name}: {str(e)}")
        
        self.documents = documents
        return documents
    
    def get_documents(self) -> List[Dict[str, str]]:
        """Return loaded documents"""
        return self.documents
