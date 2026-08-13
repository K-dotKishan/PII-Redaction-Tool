"""Tests for DOCX Processor"""
import pytest
import sys
import os
from docx import Document
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.docx_processor import DocxProcessor

def test_docx_processor_init():
    """Test processor initialization"""
    processor = DocxProcessor(use_spacy=False)
    
    assert processor.detector is not None
    assert processor.replacer is not None

def test_replace_paragraph_text():
    """Test paragraph text replacement"""
    processor = DocxProcessor(use_spacy=False)
    
    # Create a test document
    doc = Document()
    para = doc.add_paragraph("Original text")
    
    processor._replace_paragraph_text(para, "New text")
    
    assert para.text == "New text"

def test_merge_detections():
    """Test detection merging"""
    processor = DocxProcessor(use_spacy=False)
    
    all_detections = {'EMAIL': [('test1@example.com', 0, 17)]}
    new_detections = {'EMAIL': [('test2@example.com', 20, 37)], 'PHONE': [('+91 1234567890', 40, 55)]}
    
    processor._merge_detections(all_detections, new_detections)
    
    assert len(all_detections['EMAIL']) == 2
    assert 'PHONE' in all_detections
    assert len(all_detections['PHONE']) == 1

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
