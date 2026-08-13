from docx import Document
import os

print("Testing DOCX save...")
doc = Document('input/Red Herring Prospectus.docx')
print(f"Loaded: {len(doc.paragraphs)} paragraphs")

# Try to save
try:
    doc.save('output/test_output.docx')
    print("Save succeeded")
    
    if os.path.exists('output/test_output.docx'):
        size = os.path.getsize('output/test_output.docx')
        print(f"File exists: {size} bytes")
    else:
        print("ERROR: File doesn't exist after save!")
except Exception as e:
    print(f"Save failed: {e}")
    import traceback
    traceback.print_exc()
