#!/usr/bin/env python3
# Standard library imports
import os  # For file and directory operations
import re  # For regular expression pattern matching
import logging  # For application logging
from urllib.parse import urlparse, parse_qs  # For URL parsing operations

# Third-party imports
import pytesseract  # For optical character recognition
import cv2  # For image processing
import pandas as pd  # For data manipulation
from flask import Flask, render_template, request  # For web application framework
from werkzeug.utils import secure_filename  # For secure file handling
from pyzbar.pyzbar import decode  # For QR code decoding

# Constants
UPLOAD_FOLDER = 'uploaded_mcs'  # Directory to store uploaded files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}  # Set of allowed file extensions
LOG_FILE = 'mc_checker.log'  # Log file path

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,  # Log to this file
    level=logging.INFO,  # Set logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    datefmt='%Y-%m-%d %H:%M:%S'  # Date format in logs
)

# Flask application initialization
app = Flask(__name__)  # Create Flask application instance
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # Configure upload folder
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit upload size to 16MB

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"  # Set path to Tesseract executable

def setup_app() -> None:
    """
    Initialize application requirements.
    Creates necessary directories and sets up logging.
    """
    if not os.path.exists(UPLOAD_FOLDER):  # Check if upload directory exists
        os.makedirs(UPLOAD_FOLDER)  # Create directory if it doesn't exist
        logging.info(f"Created upload directory: {UPLOAD_FOLDER}")  # Log directory creation

def allowed_file(filename: str) -> bool:
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the file to check
        
    Returns:
        bool: True if file extension is allowed, False otherwise
        
    Example:
        >>> allowed_file('test.png')
        True
        >>> allowed_file('test.pdf')
        False
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS  # Check file extension

def validate_image(image_path: str) -> bool:
    """
    Validate if the file is a valid image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        bool: True if valid image, False otherwise
    """
    try:
        img = cv2.imread(image_path)  # Try to read the image
        return img is not None  # Return True if image was read successfully
    except Exception as e:
        logging.error(f"Error validating image {image_path}: {str(e)}")  # Log validation error
        return False  # Return False if any error occurs

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from image using OCR.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        str: Extracted text from image
        
    Raises:
        ValueError: If image is invalid or OCR fails
    """
    try:
        if not validate_image(image_path):  # Validate image before processing
            raise ValueError("Invalid image file")  # Raise error if image is invalid
            
        image = cv2.imread(image_path)  # Read image file
        text = pytesseract.image_to_string(image)  # Perform OCR
        logging.info(f"Successfully extracted text from {image_path}")  # Log success
        return text  # Return extracted text
    except Exception as e:
        logging.error(f"Error extracting text from {image_path}: {str(e)}")  # Log error
        raise ValueError(f"Failed to extract text: {str(e)}")  # Raise error with details

def extract_ic_from_text(text: str) -> str:
    """
    Extract IC number from text using regex.
    
    Args:
        text (str): Text to search for IC number
        
    Returns:
        str: Extracted IC number or None if not found
        
    Example:
        >>> extract_ic_from_text("Patient IC: T1234567A")
        'T1234567A'
    """
    try:
        match = re.search(r'T\d{7}[A-Z]', text)  # Search for IC pattern
        if match:
            ic = match.group(0)  # Extract matched IC
            logging.info(f"Successfully extracted IC: {ic}")  # Log success
            return ic  # Return extracted IC
        logging.warning("No IC number found in text")  # Log warning if no IC found
        return None  # Return None if no match found
    except Exception as e:
        logging.error(f"Error extracting IC from text: {str(e)}")  # Log error
        return None  # Return None on error

def extract_qr_urls(image_path: str) -> list:
    """
    Extract URLs from QR codes in image.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        list: List of decoded URLs from QR codes
    """
    try:
        image = cv2.imread(image_path)  # Read image file
        decoded_objects = decode(image)  # Decode QR codes
        qr_urls = [obj.data.decode('utf-8') for obj in decoded_objects]  # Extract URLs
        logging.info(f"Successfully extracted {len(qr_urls)} QR URLs")  # Log success
        return qr_urls  # Return list of URLs
    except Exception as e:
        logging.error(f"Error extracting QR URLs: {str(e)}")  # Log error
        return []  # Return empty list on error

def extract_ic_from_qr_url(qr_url: str) -> str:
    """
    Extract IC number from QR code URL.
    
    Args:
        qr_url (str): URL from QR code
        
    Returns:
        str: Extracted IC number or None if not found
    """
    try:
        parsed_url = urlparse(qr_url)  # Parse URL
        query_params = parse_qs(parsed_url.query)  # Extract query parameters
        ic_number = query_params.get('patient_nric', [None])[0]  # Get IC number
        if ic_number:
            logging.info(f"Successfully extracted IC from QR URL: {ic_number}")  # Log success
        return ic_number  # Return IC number
    except Exception as e:
        logging.error(f"Error extracting IC from QR URL: {str(e)}")  # Log error
        return None  # Return None on error

def verify_ic(ocr_ic: str, qr_ic: str) -> str:
    """
    Verify if IC numbers from OCR and QR code match.
    
    Args:
        ocr_ic (str): IC number from OCR
        qr_ic (str): IC number from QR code
        
    Returns:
        str: Verification result message
    """
    if not ocr_ic or not qr_ic:  # Check if both ICs are present
        msg = "❌ Could not extract IC number properly."
        logging.warning(msg)  # Log warning
        return msg  # Return error message

    if ocr_ic == qr_ic:  # Compare IC numbers
        msg = "✅ MC is Legit!"
        logging.info(msg)  # Log success
        return msg  # Return success message
    else:
        msg = "⚠️ Please verify manually. Mismatch in IC number."
        logging.warning(f"IC mismatch - OCR: {ocr_ic}, QR: {qr_ic}")  # Log mismatch
        return msg  # Return warning message

@app.route('/', methods=['GET', 'POST'])
def index() -> str:
    """
    Handle main page requests and file uploads.
    
    Returns:
        str: Rendered HTML template
    """
    if request.method == 'POST':  # Check if request is POST
        try:
            if 'mc_file' not in request.files:  # Check if file was uploaded
                logging.warning("No file part in request")  # Log warning
                return render_template('index.html', error="No file uploaded")  # Return error message

            file = request.files['mc_file']  # Get uploaded file
            if not file or not file.filename:  # Validate file existence
                logging.warning("No file selected")  # Log warning
                return render_template('index.html', error="No file selected")  # Return error message

            if not allowed_file(file.filename):  # Check file extension
                logging.warning(f"Invalid file type: {file.filename}")  # Log warning
                return render_template('index.html', error="Invalid file type")  # Return error message

            filename = secure_filename(file.filename)  # Secure the filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Create file path
            file.save(file_path)  # Save file
            logging.info(f"File saved: {file_path}")  # Log file save

            text = extract_text_from_image(file_path)  # Extract text from image
            ocr_ic = extract_ic_from_text(text)  # Extract IC from text
            qr_urls = extract_qr_urls(file_path)  # Extract QR URLs
            qr_ic = None  # Initialize QR IC

            for url in qr_urls:  # Process each QR URL
                ic_from_qr = extract_ic_from_qr_url(url)  # Extract IC from URL
                if ic_from_qr:  # Check if IC was found
                    qr_ic = ic_from_qr  # Store IC
                    break  # Exit loop

            result = verify_ic(ocr_ic, qr_ic)  # Verify IC numbers
            return render_template('index.html', result=result)  # Return result

        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")  # Log error
            return render_template('index.html', error="An error occurred")  # Return error message

    return render_template('index.html')  # Return template for GET request

if __name__ == '__main__':
    setup_app()  # Initialize application
    app.run(debug=True)  # Run Flask application in debug mode
