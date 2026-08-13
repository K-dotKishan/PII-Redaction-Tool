"""Test redaction with fixed detector"""
import sys
sys.path.insert(0, '.')

from src.docx_processor import DocxProcessor
from docx import Document
import os

print("="*70)
print("TESTING FIXED REDACTION")
print("="*70)

# Initialize with pattern-based detection only
processor = DocxProcessor(use_spacy=False)

print("\nStep 1: Testing detection on sample text...")
test_text = "Dated December 10, 2025. Please read section 32 of the Companies Act, 2013. Company Secretary: Mr. Sarthak Malvadkar"
detections = processor.detector.detect_all(test_text)

print(f"  PERSON detections: {len(detections['PERSON'])}")
if detections['PERSON']:
    print("  Detected persons:")
    for p in detections['PERSON']:
        print(f"    - {p[0]}")
else:
    print("  ✓ No false positives on 'Dated December', 'Companies Act'")

print("\nStep 2: Processing first 50 paragraphs as test...")
doc = Document('input/Red Herring Prospectus.docx')

# Process just first 50 paragraphs for quick test
test_paragraphs = []
for i, para in enumerate(doc.paragraphs[:50]):
    if para.text.strip():
        detections = processor.detector.detect_all(para.text)
        if any(detections.values()):
            redacted_text, _ = processor.replacer.replace_in_text(para.text, detections)
            test_paragraphs.append((i, para.text[:80], redacted_text[:80], detections))

print(f"\nFound {len(test_paragraphs)} paragraphs with PII in first 50")
print("\nSample redactions:")
for i, orig, redacted, dets in test_paragraphs[:5]:
    print(f"\nPara {i}:")
    print(f"  Original: {orig}")
    print(f"  Redacted: {redacted}")
    pii_counts = {k: len(v) for k, v in dets.items() if v}
    print(f"  PII: {pii_counts}")

print("\n" + "="*70)
print("If this looks correct (no 'Dated December' → name replacements),")
print("then the fix is working!")
print("="*70)
