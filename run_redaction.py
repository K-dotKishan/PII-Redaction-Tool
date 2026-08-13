"""Quick redaction script"""
import sys
sys.path.insert(0, '.')

from src.docx_processor import DocxProcessor
import time

print("="*70)
print("PII REDACTION TOOL - Processing")
print("="*70)

start_time = time.time()

processor = DocxProcessor(use_spacy=False)

print("\nInput: input/Red Herring Prospectus.docx")
print("Output: output/redacted_prospectus.docx")
print("\nProcessing... (this may take 1-2 minutes)\n")

try:
    result = processor.process_document(
        'input/Red Herring Prospectus.docx',
        'output/redacted_prospectus.docx'
    )
    
    elapsed = time.time() - start_time
    
    print("\n" + "="*70)
    print("REDACTION COMPLETE")
    print("="*70)
    print(f"\nTime elapsed: {elapsed:.1f} seconds")
    print(f"\nStatistics:")
    for pii_type, count in sorted(result['statistics'].items()):
        if count > 0:
            print(f"  {pii_type}: {count}")
    
    print("\n" + "="*70)
    
    # Verify output
    verification = processor.verify_redaction('output/redacted_prospectus.docx')
    if verification['success']:
        print("✓ Output file created successfully")
        print(f"✓ File is readable: {verification['file_readable']}")
        print(f"✓ Paragraphs: {verification['paragraphs']}")
        print(f"✓ Tables: {verification['tables']}")
        
        if verification['verification_passed']:
            print("✓ Post-redaction scan: PASSED")
        else:
            print(f"⚠ Remaining PII detected: {verification['remaining_pii']}")
            print("  (May include false positives or generated fake values)")
    
    print("="*70)
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    import traceback
    traceback.print_exc()
