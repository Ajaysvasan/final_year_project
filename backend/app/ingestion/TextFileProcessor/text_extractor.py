import os
from pathlib import Path
from typing import Dict


class TextExtractor:
    def __init__(self):
        pass

    def _extract_from_txt(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as file:
                    return file.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return ""
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    def _extract_from_docx(self, file_path: str) -> str:
        try:
            from docx import Document

            doc = Document(file_path)
            full_text = []
            for paragraph in doc.paragraphs:
                full_text.append(paragraph.text)
            return "\n".join(full_text)
        except ImportError:
            print(
                "Error: python-docx library not installed. Run: pip install python-docx"
            )
            return ""
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    def _extract_from_doc(self, file_path: str) -> str:
        try:
            import textract

            text = textract.process(file_path).decode("utf-8")
            return text
        except ImportError:
            print("Error: textract library not installed. Run: pip install textract")
            print("Note: textract may require additional system dependencies")
            return ""
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    def _extract_from_pdf(self, file_path: str) -> str:
        try:
            import PyPDF2

            text = []
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
            return "\n".join(text)
        except ImportError:
            print("Error: PyPDF2 library not installed. Run: pip install PyPDF2")
            return ""
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""

    def __extract_text_from_md(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise Exception(f"The Path {file_path} does not exists")
        text = []
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.readlines()

        return "\n".join(text)

    def extract_text_from_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            print(f"Error: File does not exist: {file_path}")
            return ""

        extension = Path(file_path).suffix.lower()

        if extension == ".txt":
            return self._extract_from_txt(file_path)
        elif extension == ".docx":
            return self._extract_from_docx(file_path)
        elif extension == ".doc":
            return self._extract_from_doc(file_path)
        elif extension == ".pdf":
            return self._extract_from_pdf(file_path)
        elif extension == ".md":
            return self.__extract_text_from_md(file_path)
        else:
            print(f"Unsupported file type: {extension}")
            return ""

    def extract_all(self, loaded_files: Dict[str, list]) -> Dict[str, str]:
        extracted_texts = {}

        for category, file_paths in loaded_files.items():
            print(category)
            for file_path in file_paths:
                print(f"Processing: {file_path}")
                text = self.extract_text_from_file(file_path)
                extracted_texts[file_path] = text

        return extracted_texts
