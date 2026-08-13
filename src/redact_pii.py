"""Main PII Redaction Script"""
import argparse
import os
import sys
from .docx_processor import DocxProcessor
from .config import PII_CATEGORIES

def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description='Redact PII from DOCX documents')
    parser.add_argument('--input', required=True, help='Input DOCX file path')
    parser.add_argument('--output', required=True, help='Output DOCX file path')
    parser.add_argument('--no-spacy', action='store_true', help='Disable spaCy NER')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(1)
    
    if not args.input.lower().endswith('.docx'):
        print(f"Error: Input file must be a DOCX file")
        sys.exit(1)
    
    # Create output directory if needed
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process document
    print("=" * 70)
    print("PII REDACTION TOOL")
    print("=" * 70)
    
    processor = DocxProcessor(use_spacy=not args.no_spacy)
    
    try:
        result = processor.process_document(args.input, args.output)
        
        # Print statistics
        print("\n" + "=" * 70)
        print("REDACTION SUMMARY")
        print("=" * 70)
        print(f"\n{'PII Type':<20} {'Unique Values Detected':<25}")
        print("-" * 45)
        
        for pii_type in PII_CATEGORIES:
            count = result['statistics'].get(pii_type, 0)
            print(f"{pii_type:<20} {count:<25}")
        
        total = sum(result['statistics'].values())
        print("-" * 45)
        print(f"{'TOTAL':<20} {total:<25}")
        
        print("\n" + "=" * 70)
        print(f"✓ Redacted document saved: {args.output}")
        print("=" * 70)
        
        # Verify redaction
        verification = processor.verify_redaction(args.output)
        
        if verification['success']:
            print(f"\n✓ Output file is readable")
            print(f"✓ Paragraphs: {verification['paragraphs']}")
            print(f"✓ Tables: {verification['tables']}")
            
            if verification['verification_passed']:
                print(f"✓ Post-redaction scan: PASSED (no obvious PII detected)")
            else:
                print(f"⚠ Post-redaction scan: Some potential PII detected")
                print(f"  Remaining: {verification['remaining_pii']}")
                print(f"  Note: These may be false positives or newly generated fake values")
        else:
            print(f"\n✗ Error verifying output: {verification.get('error')}")
        
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error processing document: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
