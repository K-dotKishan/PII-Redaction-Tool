"""Flask Web Application for PII Redaction Tool"""
from flask import Flask, render_template, request, send_file, jsonify
import os
import sys
import tempfile
import uuid
from werkzeug.utils import secure_filename

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.docx_processor import DocxProcessor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Initialize processor
processor = DocxProcessor(use_spacy=False)

ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and redaction"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only DOCX files are allowed'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_id = str(uuid.uuid4())
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}_input.docx')
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}_output.docx')
        
        file.save(input_path)
        
        # Process document
        result = processor.process_document(input_path, output_path)
        
        # Clean up input file
        if os.path.exists(input_path):
            os.remove(input_path)
        
        # Return statistics and download link
        return jsonify({
            'success': True,
            'file_id': file_id,
            'statistics': result['statistics'],
            'message': 'Document redacted successfully'
        })
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
        
        return jsonify({'error': f'Error processing document: {str(e)}'}), 500

@app.route('/download/<file_id>')
def download_file(file_id):
    """Download redacted file"""
    try:
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{file_id}_output.docx')
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(
            output_path,
            as_attachment=True,
            download_name='redacted_document.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    except Exception as e:
        return jsonify({'error': f'Error downloading file: {str(e)}'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
