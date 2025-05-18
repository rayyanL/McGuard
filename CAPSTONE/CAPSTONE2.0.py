# 
# Standard library imports
import os
import re
import logging
from urllib.parse import urlparse, parse_qs

# Third-party imports
import pytesseract
import cv2
import pandas as pd
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path

# Constants
UPLOAD_FOLDER = 'uploaded_mcs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
LOG_FILE = 'mc_checker.log'

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Flask setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Set tesseract path (customize this if needed)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"  # or '/usr/bin/tesseract' for Linux

def setup_app():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        logging.info(f"Created upload directory: {UPLOAD_FOLDER}")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(image_path):
    try:
        img = cv2.imread(image_path)
        return img is not None
    except Exception as e:
        logging.error(f"Error validating image {image_path}: {str(e)}")
        return False

def convert_pdf_to_image(pdf_path):
    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        image_path = pdf_path + ".jpg"
        images[0].save(image_path, 'JPEG')
        logging.info(f"Converted PDF to image: {image_path}")
        return image_path
    except Exception as e:
        logging.error(f"Failed to convert PDF to image: {str(e)}")
        raise ValueError("PDF conversion failed")

def extract_text_from_image(image_path):
    try:
        if not validate_image(image_path):
            raise ValueError("Invalid image file")
        image = cv2.imread(image_path)
        text = pytesseract.image_to_string(image)
        logging.info(f"Successfully extracted text from {image_path}")
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {image_path}: {str(e)}")
        raise ValueError(f"Failed to extract text: {str(e)}")

def extract_ic_from_text(text):
    try:
        match = re.search(r'T\d{7}[A-Z]', text)
        if match:
            ic = match.group(0)
            logging.info(f"Successfully extracted IC: {ic}")
            return ic
        logging.warning("No IC number found in text")
        return None
    except Exception as e:
        logging.error(f"Error extracting IC from text: {str(e)}")
        return None

def extract_qr_urls(image_path):
    try:
        image = cv2.imread(image_path)
        decoded_objects = decode(image)
        qr_urls = [obj.data.decode('utf-8') for obj in decoded_objects]
        logging.info(f"Successfully extracted {len(qr_urls)} QR URLs")
        return qr_urls
    except Exception as e:
        logging.error(f"Error extracting QR URLs: {str(e)}")
        return []

def extract_ic_from_qr_url(qr_url):
    try:
        parsed_url = urlparse(qr_url)
        query_params = parse_qs(parsed_url.query)
        ic_number = query_params.get('patient_nric', [None])[0]
        if ic_number:
            logging.info(f"Successfully extracted IC from QR URL: {ic_number}")
        return ic_number
    except Exception as e:
        logging.error(f"Error extracting IC from QR URL: {str(e)}")
        return None

def verify_ic(ocr_ic, qr_ic):
    if not ocr_ic or not qr_ic:
        msg = "❌ Could not extract IC number properly."
        logging.warning(msg)
        return msg

    if ocr_ic == qr_ic:
        msg = "✅ MC is Legit!"
        logging.info(msg)
        return msg
    else:
        msg = "⚠️ Please verify manually. Mismatch in IC number."
        logging.warning(f"IC mismatch - OCR: {ocr_ic}, QR: {qr_ic}")
        return msg

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            if 'mc_file' not in request.files:
                logging.warning("No file part in request")
                return render_template('index.html', error="No file uploaded")

            file = request.files['mc_file']
            if not file or not file.filename:
                logging.warning("No file selected")
                return render_template('index.html', error="No file selected")

            if not allowed_file(file.filename):
                logging.warning(f"Invalid file type: {file.filename}")
                return render_template('index.html', error="Invalid file type")

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            logging.info(f"File saved: {file_path}")

            # Handle PDF conversion
            if filename.lower().endswith('.pdf'):
                image_path = convert_pdf_to_image(file_path)
            else:
                image_path = file_path

            text = extract_text_from_image(image_path)
            ocr_ic = extract_ic_from_text(text)
            qr_urls = extract_qr_urls(image_path)

            qr_ic = None
            for url in qr_urls:
                ic_from_qr = extract_ic_from_qr_url(url)
                if ic_from_qr:
                    qr_ic = ic_from_qr
                    break

            result = verify_ic(ocr_ic, qr_ic)
            return render_template('index.html', result=result)

        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            return render_template('index.html', error="An error occurred")

    return render_template('index.html')

if __name__ == '__main__':
    setup_app()
    app.run(debug=True)


# streamlit run CAPSTONE/CAPSTONE2.0.py
