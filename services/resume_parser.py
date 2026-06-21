import os
import re
import PyPDF2
import pdfplumber

class ResumeParser:
    @staticmethod
    def extract_text(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at {file_path}")
        
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            pass

        if not text.strip():
            try:
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception as e:
                raise RuntimeError(f"Failed to parse PDF variants: {str(e)}")
        
        return text

    @staticmethod
    def extract_candidate_name(text: str, filename: str) -> str:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line.split()) <= 4 and not re.search(r'(resume|cv|curriculum|vitae)', first_line, re.IGNORECASE):
                return first_line
        
        name_match = re.search(r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})", text)
        if name_match:
            return name_match.group(1)
            
        clean_name = os.path.splitext(filename)[0]
        clean_name = re.sub(r'[_--------]', ' ', clean_name)
        return clean_name.title()