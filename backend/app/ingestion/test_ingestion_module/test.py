import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from pathlib import Path

from ingestion.Chunker.normalizer import NORMALIZATION_VERSION, NormalizationProfiles
from ingestion.TextFileProcessor.file_loader import FileLoader
from ingestion.TextFileProcessor.text_extractor import TextExtractor

data_path = (
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
) + "/dataset"
file_loader = FileLoader(data_path)
loaded_files = file_loader.load_files()

print(f"Found files: {loaded_files}")
print("\n" + "=" * 50 + "\n")

extractor = TextExtractor()
extracted_texts = extractor.extract_all(loaded_files)

for file_path, text in extracted_texts.items():
    print(f"File: {file_path}")
    print(f"Text length: {len(text)} characters")
    print(f"Preview: {text[:200]}...")


print(f"Using normalization version: {NORMALIZATION_VERSION}")
file_loader = FileLoader(data_path)
loaded_files = file_loader.load_files()

extractor = TextExtractor()
extracted_texts = extractor.extract_all(loaded_files)

# Use the fixed RAG ingestion policy
normalizer = NormalizationProfiles.rag_ingestion()
normalized_texts = normalizer.normalize_all(extracted_texts)

for file_path, text in normalized_texts.items():
    print(f"File: {file_path}")
    print(f"Text length: {len(text)} characters")
    print(f"Preview: {text[:200]}...")

sample_text = (
    "Contact us at support@example.com or visit https://example.com.\n\n"
    "Our office is at 123 Main St. Price: $99.99\n"
    "More info at www.docs.example.com"
)
print(f"\nOriginal:\n{sample_text}")
print(f"\nNormalized:\n{normalizer.normalize_text(sample_text)}")
