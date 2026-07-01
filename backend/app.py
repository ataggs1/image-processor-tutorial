from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import uuid
import json
import base64
import io
from pathlib import Path
from datetime import datetime
from processor import ImageProcessor
from PIL import Image


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if filename has an allowed extension.

    Args:
        filename: Name of the file to check
        allowed_extensions: Set of allowed file extensions (without dots)

    Returns:
        True if file has allowed extension, False otherwise
    """
    if not filename or '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    CORS(app)

    # Load configuration from environment variables
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    PROCESSED_FOLDER = os.getenv('PROCESSED_FOLDER', 'processed')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB default
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif').split(','))

    # Store config in app for access in routes
    app.config['MAX_FILE_SIZE'] = MAX_FILE_SIZE

    # Create directories if they don't exist
    Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(PROCESSED_FOLDER).mkdir(parents=True, exist_ok=True)

    # Initialize ImageProcessor
    processor = ImageProcessor()

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({"status": "healthy"})

    @app.route('/process', methods=['POST'])
    def process_image():
        """Process uploaded image with specified operations"""
        try:
            # Check file size
            if request.content_length and request.content_length > app.config['MAX_FILE_SIZE']:
                return jsonify({
                    "error": f"File too large. Maximum size: {app.config['MAX_FILE_SIZE']} bytes"
                }), 413

            # Check if file was uploaded
            if 'file' not in request.files:
                return jsonify({"error": "No file provided"}), 400

            file = request.files['file']

            # Check if filename is empty
            if file.filename == '':
                return jsonify({"error": "No file selected"}), 400

            # Validate file extension
            if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
                return jsonify({
                    "error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                }), 400

            # Get operations from request
            operations_json = request.form.get('operations', '[]')
            operations = json.loads(operations_json)

            # Load image with PIL
            image = Image.open(file.stream)
            original_width, original_height = image.size

            # Store original dimensions
            processed_image = image.copy()

            # Apply operations
            for op in operations:
                operation = op.get('operation')
                params = op.get('params', {})

                if operation == 'resize':
                    width = params.get('width')
                    height = params.get('height')
                    # Validate resize parameters
                    if width is None or height is None:
                        return jsonify({
                            "error": "Resize operation requires 'width' and 'height' parameters"
                        }), 400
                    if not isinstance(width, int) or not isinstance(height, int):
                        return jsonify({
                            "error": "Width and height must be integers"
                        }), 400
                    if width <= 0 or height <= 0:
                        return jsonify({
                            "error": "Width and height must be positive integers"
                        }), 400
                    processed_image = processor.resize(processed_image, width, height)

                elif operation == 'grayscale':
                    processed_image = processor.convert_grayscale(processed_image)

                elif operation == 'blur':
                    radius = params.get('radius', 5)
                    processed_image = processor.apply_blur(processed_image, radius)

                elif operation == 'thumbnail':
                    max_size = params.get('max_size', 200)
                    processed_image = processor.create_thumbnail(processed_image, max_size)

            # Generate unique filename
            unique_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{unique_id}.png"

            # Save original image
            original_path = Path(UPLOAD_FOLDER) / filename
            image.save(original_path, 'PNG')

            # Save processed image
            processed_path = Path(PROCESSED_FOLDER) / filename
            processed_image.save(processed_path, 'PNG')

            # Convert processed image to base64
            buffered = io.BytesIO()
            processed_image.save(buffered, format='PNG')
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            img_data_url = f"data:image/png;base64,{img_base64}"

            # Get processed dimensions
            processed_width, processed_height = processed_image.size

            # Build response
            response_data = {
                "processed_image": img_data_url,
                "metadata": {
                    "original_dimensions": [original_width, original_height],
                    "processed_dimensions": [processed_width, processed_height],
                    "filename": filename,
                    "timestamp": timestamp,
                    "operations_applied": len(operations)
                }
            }

            return jsonify(response_data), 200

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": f"Processing failed: {str(e)}"}), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
