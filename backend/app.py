from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import logging
from linkedin_parser import LinkedInParser
from cv_generator import CVGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS Configuration - Allow localhost on any port and file:// protocol (origin: null)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:*",
            "http://localhost:8080",
            "http://127.0.0.1:*",
            "http://127.0.0.1:8080",
            "null"  # For direct file:// access
        ],
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": False
    }
})

# Configuration
UPLOAD_FOLDER = '/tmp/cv_uploads'
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
MAX_TOTAL_SIZE = 50 * 1024 * 1024  # 50MB total
ALLOWED_EXTENSIONS = {'csv'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB for images

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_secure_filepath(original_filename):
    """Generate secure filepath to prevent path traversal"""
    # Secure the filename
    secured_name = secure_filename(original_filename)

    # Generate unique filename to avoid collisions
    unique_id = uuid.uuid4().hex

    # Extract basename and extension
    if '.' in secured_name:
        basename = secured_name.rsplit('.', 1)[0]
        extension = secured_name.rsplit('.', 1)[1].lower()
    else:
        basename = secured_name
        extension = 'csv'

    # Keep original basename for parser recognition, add UUID for uniqueness
    safe_filename = f"{basename}_{unique_id}.{extension}"

    return os.path.join(UPLOAD_FOLDER, safe_filename)

@app.route('/')
def index():
    return jsonify({"message": "CV Generator API", "status": "running", "version": "1.0"})

@app.route('/api/parse-linkedin', methods=['POST'])
def parse_linkedin():
    """Parse LinkedIn export files with security validation"""
    saved_files = []

    try:
        if 'files' not in request.files:
            logger.warning("No files in request")
            return jsonify({"error": "No files uploaded"}), 400

        files = request.files.getlist('files')

        if not files:
            return jsonify({"error": "No files uploaded"}), 400

        # Validate number of files
        if len(files) > 20:
            return jsonify({"error": "Too many files. Maximum 20 files allowed"}), 400

        # Calculate total size
        total_size = 0
        for file in files:
            if file.filename:
                # Seek to end to get size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)  # Reset to beginning

                total_size += file_size

                # Validate individual file size
                if file_size > MAX_FILE_SIZE:
                    return jsonify({
                        "error": f"File '{file.filename}' is too large. Maximum {MAX_FILE_SIZE // (1024*1024)}MB per file"
                    }), 400

        # Validate total size
        if total_size > MAX_TOTAL_SIZE:
            return jsonify({
                "error": f"Total upload size exceeds limit. Maximum {MAX_TOTAL_SIZE // (1024*1024)}MB"
            }), 400

        # Save files temporarily with validation
        for file in files:
            if file.filename:
                # Validate file extension
                if not allowed_file(file.filename):
                    return jsonify({
                        "error": f"Invalid file type for '{file.filename}'. Only CSV files allowed"
                    }), 400

                # Generate secure filepath
                filepath = get_secure_filepath(file.filename)

                # Save file
                file.save(filepath)
                saved_files.append(filepath)
                logger.info(f"Saved file: {file.filename} as {os.path.basename(filepath)}")

        if not saved_files:
            return jsonify({"error": "No valid files uploaded"}), 400

        # Parse LinkedIn data
        parser = LinkedInParser(saved_files)
        data = parser.parse()

        logger.info(f"Successfully parsed {len(saved_files)} files")

        return jsonify(data)

    except Exception as e:
        logger.error(f"Error parsing LinkedIn data: {e}", exc_info=True)
        return jsonify({"error": "Failed to parse LinkedIn data", "details": str(e)}), 500

    finally:
        # Always clean up temporary files
        for filepath in saved_files:
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
                    logger.debug(f"Cleaned up: {filepath}")
            except Exception as e:
                logger.error(f"Failed to cleanup file {filepath}: {e}")

@app.route('/api/generate-pdf', methods=['POST'])
def generate_pdf():
    """Generate PDF from parsed data with validation"""
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Validate data structure
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid data format"}), 400

        # Validate photo size if present
        if 'photo' in data and data['photo']:
            photo_data = data['photo']

            # Remove data URL prefix if present
            if 'base64,' in photo_data:
                photo_data = photo_data.split('base64,')[1]

            # Estimate size (base64 is ~33% larger than binary)
            import base64
            try:
                estimated_size = len(photo_data) * 3 // 4
                if estimated_size > MAX_IMAGE_SIZE:
                    return jsonify({
                        "error": f"Photo too large. Maximum {MAX_IMAGE_SIZE // (1024*1024)}MB"
                    }), 400
            except Exception:
                return jsonify({"error": "Invalid photo data"}), 400

        # Extract config if provided
        config = data.pop('config', None) if 'config' in data else None

        # Generate PDF with config
        generator = CVGenerator(data, config=config)
        pdf_path = generator.generate()

        logger.info("PDF generated successfully")

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
            try:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    logger.debug(f"Cleaned up PDF: {pdf_path}")
            except Exception as e:
                logger.error(f"Failed to cleanup PDF {pdf_path}: {e}")

        return response

    except Exception as e:
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        return jsonify({"error": "Failed to generate PDF", "details": str(e)}), 500

if __name__ == '__main__':
    # Production-safe configuration
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '127.0.0.1')  # Localhost only by default
    port = int(os.getenv('FLASK_PORT', '5000'))

    if debug_mode:
        logger.warning("Running in DEBUG mode - not suitable for production!")

    logger.info(f"Starting CV Generator API on {host}:{port}")
    app.run(debug=debug_mode, host=host, port=port)
