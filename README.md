# PII Redaction Tool

A comprehensive Python-based tool for automatically detecting and redacting Personally Identifiable Information (PII) from DOCX documents.

## 📋 Assignment Overview

This project was developed for the Scaler AI Labs PII Redaction Tool assignment. The tool processes a Red Herring Prospectus (financial document) and replaces all detected PII with realistic fake values while preserving document structure and formatting.

## ✨ Features

- **Comprehensive PII Detection**: Detects 9 categories of PII
- **Hybrid Detection Approach**: Combines regex patterns, NER (when available), and contextual rules
- **Consistent Replacements**: Same PII value always gets the same fake replacement
- **DOCX Preservation**: Maintains document structure, formatting, tables, and paragraphs
- **CLI & Web Interface**: Both command-line and web-based interfaces
- **Automated Testing**: Comprehensive test suite with pytest
- **Evaluation Framework**: Calculates precision, recall, F1, and accuracy metrics
- **Cloud Deployable**: Ready for deployment on Render, Railway, or similar platforms

## 🎯 Supported PII Types

1. **PERSON** - Full names of individuals
2. **EMAIL** - Email addresses
3. **PHONE** - Phone numbers (Indian and international formats)
4. **COMPANY** - Company and organization names
5. **ADDRESS** - Physical/mailing addresses
6. **SSN** - Social Security Numbers
7. **CREDIT_CARD** - Credit card numbers (with Luhn validation)
8. **DOB** - Dates of birth (context-aware)
9. **IP** - IPv4 addresses

## 🏗️ Architecture

### Project Structure

```
PII-Redaction-Tool/
├── input/
│   └── Red Herring Prospectus.docx  # Original document (contains PII)
├── output/
│   └── redacted_prospectus.docx     # Redacted output (generated)
├── src/
│   ├── __init__.py
│   ├── config.py                    # Configuration and patterns
│   ├── detector.py                  # PII detection logic
│   ├── replacer.py                  # PII replacement logic
│   ├── docx_processor.py            # DOCX file processing
│   └── redact_pii.py                # Main CLI script
├── web/
│   ├── app.py                       # Flask web application
│   ├── templates/
│   │   └── index.html               # Web UI
│   └── static/
│       └── style.css                # Styling
├── tests/
│   ├── test_detector.py             # Detector tests
│   ├── test_replacer.py             # Replacer tests
│   └── test_docx_processor.py       # DOCX processor tests
├── evaluation/
│   ├── evaluate.py                  # Evaluation script
│   ├── ground_truth.json            # Annotated ground truth
│   └── evaluation_results.txt       # Evaluation metrics (generated)
├── requirements.txt
├── Procfile                         # For deployment
├── render.yaml                      # Render configuration
└── README.md
```

### Technology Stack

- **Python 3.11+**: Core programming language
- **python-docx**: DOCX file reading and writing
- **Faker**: Generating realistic fake PII values
- **Flask**: Web application framework
- **Gunicorn**: Production WSGI server
- **pytest**: Testing framework
- **spaCy** (optional): Named Entity Recognition

## 🔍 Detection Approach

The tool uses a **hybrid approach** combining multiple techniques:

### 1. Regex-Based Detection

Used for structured PII with predictable patterns:
- **Emails**: Validates email format with domain extensions
- **Phone Numbers**: Supports Indian (+91) and international formats
- **IP Addresses**: Validates IPv4 octets (0-255 range)
- **SSN**: Detects XXX-XX-XXXX format
- **Credit Cards**: 13-19 digit numbers with Luhn algorithm validation

### 2. Named Entity Recognition (NER)

Uses spaCy (when available) for contextual detection:
- **PERSON entities**: Detects individual names
- **ORG entities**: Identifies organizations
- **GPE/LOC entities**: Recognizes locations for address detection

Falls back to pattern-based detection if spaCy is unavailable.

### 3. Contextual Rules

Applies domain-specific logic to reduce false positives:
- **DOB Detection**: Only flags dates near keywords like "Date of Birth", "DOB", "Born"
- **Company Names**: Looks for indicators (Limited, Ltd., Pvt. Ltd., Inc., Corp.)
- **Financial Context**: Avoids flagging financial figures as credit cards or phones
- **Address Assembly**: Combines multiple lines with address indicators

### 4. Validation Rules

- **Credit Cards**: Luhn algorithm to validate card numbers
- **IP Addresses**: Validates octet ranges (0-255)
- **Phone Numbers**: Requires 10-15 digits to avoid false positives

## 🔄 Replacement Strategy

### Deterministic Replacement

The tool maintains a **replacement map** to ensure consistency:
- Same original value → Same fake replacement (within a single run)
- Different original values → Different fake replacements
- Prevents replacing already-replaced fake values

### Replacement Examples

| PII Type | Original | Replacement |
|----------|----------|-------------|
| PERSON | Mr. Sarthak Malvadkar | Mr. John Anderson |
| EMAIL | cs.connect@kshinternational.com | kathy.thornton@roberts.com |
| PHONE | +91 20 4505 3237 | +91 98765 43210 |
| COMPANY | Non-protected Company Ltd | Example Industries Limited |
| ADDRESS | 123 Sample Street, Pune | 456 Example Road, City |
| IP | 192.168.1.20 | 203.0.113.10 |
| SSN | 123-45-6789 | 987-65-4321 |
| CREDIT_CARD | 4111 1111 1111 1111 | 4000 0000 0000 0002 |
| DOB | DOB: 01/01/1990 | DOB: 15/06/1988 |

**Protected Entities (NOT anonymized):**
- Main company: KSH International Limited and all subsidiaries
- Business partners: ICICI Bank, HDFC Bank, Nuvama, CARE Ratings, etc.
- Generic references: "Our Company", "The Company", "The Board"
- Legal/regulatory entities: SEBI, Companies Act, BSE, NSE
- All business/legal/financial terminology

### Format Preservation

- Phone numbers maintain country code format
- Credit cards preserve spacing/hyphen patterns
- Dates match original separator (/ or -)
- Company names retain suffixes (Limited, Pvt. Ltd., etc.)

## 📦 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Setup Steps

1. **Clone or download the repository**

```bash
cd PII-Redaction-Tool
```

2. **Create virtual environment**

```bash
python -m venv .venv
```

3. **Activate virtual environment**

Windows:
```bash
.venv\Scripts\activate
```

Linux/Mac:
```bash
source .venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Optional: Install spaCy model for improved NER**

```bash
python -m spacy download en_core_web_sm
```

> **Note**: The tool works without spaCy by using pattern-based detection.

## 🚀 Usage

### Command Line Interface (CLI)

Run the redaction tool from the command line:

```bash
python -m src.redact_pii --input "input/Red Herring Prospectus.docx" --output "output/redacted_prospectus.docx"
```

**Options:**
- `--input`: Path to input DOCX file (required)
- `--output`: Path to output DOCX file (required)
- `--no-spacy`: Disable spaCy NER (optional)

**Output:**

The CLI displays:
- Processing progress
- Detection statistics by PII type
- Post-redaction verification results
- Output file location

### Web Application

Run the Flask web application locally:

```bash
python web/app.py
```

Then open your browser to: `http://localhost:5000`

**Web Interface Features:**
- Upload DOCX files (up to 50MB)
- Real-time processing with progress indicator
- Statistics display by PII category
- Download redacted document
- Error handling and validation

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

**Test Coverage:**
- Email detection and validation
- Phone number detection (various formats)
- IP address validation
- Credit card Luhn validation
- SSN detection
- DOB context-aware detection
- Person and company name detection
- Replacement consistency
- Deduplication logic

Run specific test file:

```bash
pytest tests/test_detector.py -v
```

## 📊 Evaluation

### Run Evaluation

Execute the evaluation script:

```bash
python evaluation/evaluate.py
```

This will:
1. Load ground truth annotations
2. Run detection on the input document
3. Calculate metrics (TP, FP, FN, precision, recall, F1)
4. Generate evaluation report

### Evaluation Methodology

**Metrics Calculated:**
- **True Positives (TP)**: Correctly detected PII
- **False Positives (FP)**: Incorrectly flagged as PII
- **False Negatives (FN)**: Missed PII instances
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1 Score**: 2 × (Precision × Recall) / (Precision + Recall)
- **Accuracy**: TP / (TP + FP + FN)

**Matching Criteria:**
- Exact text match between detected and ground truth values
- Per-PII-type evaluation
- Overall aggregate metrics

### Evaluation Results

See `evaluation_report.md` for detailed evaluation results.

## 📄 DOCX Processing

### Input Requirements

- File format: **Microsoft Word DOCX** (.docx)
- Must be a valid DOCX file (not .doc, .pdf, .txt)
- Can contain paragraphs, tables, headers, footers

### Processing Details

1. **Document Loading**: Uses python-docx to parse DOCX structure
2. **Text Extraction**: Processes paragraphs and table cells separately
3. **PII Detection**: Scans all text content
4. **Replacement**: Applies redactions while preserving formatting
5. **Document Saving**: Generates valid DOCX output

### Format Preservation

- ✅ Paragraphs maintained
- ✅ Tables preserved
- ✅ Basic text formatting retained
- ✅ Document structure intact
- ⚠️ Complex formatting (images, charts) may be affected

### Output Verification

After processing, the tool automatically:
1. Confirms file exists with .docx extension
2. Verifies file is readable by python-docx
3. Performs post-redaction PII scan
4. Reports any remaining PII (may be false positives or fake values)

## 🌐 Deployment

### Deploy to Render

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Create Render Service**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect `render.yaml`

3. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn web.app:app`
   - Environment: Python 3

4. **Deploy**: Render will build and deploy automatically

### Deploy to Railway/Other Platforms

The application uses standard Python deployment:
- `requirements.txt` for dependencies
- `Procfile` for process definition
- Environment variable `PORT` for port binding
- Binds to `0.0.0.0` for external access

## ⚖️ Tradeoffs

### Design Decisions

1. **Pattern-based + NER Hybrid**
   - **Pro**: Better accuracy than regex alone
   - **Pro**: Works without NER as fallback
   - **Con**: May require model download for best results

2. **Exact Replacement (Not Masking)**
   - **Pro**: More realistic fake data
   - **Pro**: Document remains readable
   - **Con**: Doesn't visually highlight redactions

3. **Conservative Financial Context**
   - **Pro**: Avoids redacting financial figures
   - **Con**: May miss some edge cases

4. **Context-Aware DOB Detection**
   - **Pro**: Doesn't redact every date
   - **Con**: May miss DOBs without clear context

## ⚠️ False Positives

Potential false positives observed:

1. **Company Names**: May flag legitimate company references that should remain
2. **Financial Numbers**: Very long numbers in financial context might trigger credit card detection
3. **Proper Nouns**: Place names or product names might be flagged as person names
4. **Generated Fake Values**: Post-redaction scan detects new fake emails/names

## ❌ False Negatives

Potential false negatives:

1. **Uncommon Formats**: Non-standard phone number formats
2. **Partial Addresses**: Incomplete address information
3. **Embedded PII**: PII within longer strings or URLs
4. **Multi-Run Text**: PII spanning multiple formatting runs in DOCX
5. **Contextless DOB**: Dates of birth without "DOB" or similar keywords

## 🔒 Limitations

1. **DOCX Only**: Does not support .doc, .pdf, or other formats
2. **English Language**: Optimized for English text
3. **Complex Formatting**: May not perfectly preserve all formatting nuances
4. **Embedded Objects**: Images, charts, and embedded objects not processed
5. **Performance**: Large documents (>100 pages) may take time to process
6. **PII Categories**: Limited to the 9 defined categories

## 🚀 Future Improvements

1. **Multi-format Support**: Add PDF, .doc, .txt support
2. **Enhanced NER**: Fine-tune models on financial documents
3. **Multi-language**: Support for non-English documents
4. **Visual Highlighting**: Option to highlight redactions
5. **Batch Processing**: Process multiple documents at once
6. **API Endpoints**: RESTful API for integration
7. **Configurable Rules**: User-defined PII patterns
8. **Audit Trail**: Detailed logging of all redactions
9. **Undo/Review**: Manual review before finalizing
10. **Performance**: Parallel processing for large documents

## 📝 Assignment Deliverables

### Input
- **File**: `input/Red Herring Prospectus.docx`
- **Type**: Original Red Herring Prospectus containing PII

### Output
- **File**: `output/redacted_prospectus.docx`
- **Type**: Redacted DOCX with PII replaced by fake values
- **Format**: Valid Microsoft Word DOCX file
- **Verification**: Can be opened in Microsoft Word/WPS Office

### Documentation
- **README.md**: This file - complete project documentation
- **evaluation_report.md**: Detailed evaluation metrics and analysis

### Code
- Complete source code in `src/` directory
- Web application in `web/` directory
- Test suite in `tests/` directory
- Evaluation framework in `evaluation/` directory

### Deployment
- Procfile and render.yaml for cloud deployment
- Requirements.txt for dependency management

## 📊 Submission Checklist

For Scaler AI Labs Google Form:

- ✅ Source code (GitHub repository)
- ✅ Redacted output DOCX file: `output/redacted_prospectus.docx`
- ✅ README.md explaining approach
- ✅ Evaluation report with metrics
- ✅ Cloud deployment (Render/Railway URL)
- ✅ Regex + NER detection approach documented
- ✅ Third-party libraries listed (python-docx, Faker, spaCy, Flask)
- ✅ Tradeoffs documented
- ✅ False positives/negatives analyzed

## 👤 Author

Developed for Scaler AI Labs PII Redaction Tool Assignment

## 📄 License

This project is created for educational and assignment purposes.

---

**Note**: The original Red Herring Prospectus contains actual PII. Handle with care and do not expose it publicly without proper authorization.
