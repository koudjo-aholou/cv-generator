from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from linkedin_parser import LinkedInParser
from cv_generator import CVGenerator

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = '/tmp/cv_uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return jsonify({"message": "CV Generator API", "status": "running"})

@app.route('/api/parse-linkedin', methods=['POST'])
def parse_linkedin():
    """Parse LinkedIn export files"""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No files uploaded"}), 400

        files = request.files.getlist('files')

        # Save files temporarily
        saved_files = []
        for file in files:
            if file.filename:
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                saved_files.append(filepath)

        # Parse LinkedIn data
        parser = LinkedInParser(saved_files)
        data = parser.parse()

        # Clean up temporary files
        for filepath in saved_files:
            if os.path.exists(filepath):
                os.remove(filepath)

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF from parsed data"""
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Generate PDF
        generator = CVGenerator(data)
        pdf_path = generator.generate()

        # Send file and clean up
        response = send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='cv.pdf'
        )

        # Clean up after sending
        @response.call_on_close
        def cleanup():
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
