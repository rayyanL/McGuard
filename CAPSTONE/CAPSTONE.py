

import os
import re
import cv2
import pytesseract
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pyzbar.pyzbar import decode

# Configuration
UPLOAD_FOLDER = 'uploaded_mcs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Tesseract path for macOS (adjust if needed)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# Helper: Check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper: OCR text extraction
def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    text = pytesseract.image_to_string(image)
    print("Extracted Text:", text)
    return text

# Helper: Extract IC number (e.g. T0721279D)
def extract_ic_number(text):
    match = re.search(r'T\d{7}[A-Z]', text)
    return match.group(0) if match else None

# Helper: Decode all QR codes
def extract_qr_data(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    qr_data_list = [obj.data.decode('utf-8') for obj in decoded_objects]
    print("Extracted QR Data:", qr_data_list)
    return qr_data_list

# Helper: Check if IC number is in any QR data string
def verify_ic_in_qr(qr_data_list, ic_number):
    for qr_data in qr_data_list:
        if ic_number in qr_data:
            return "✅ MC is Legit!"
    return "⚠️ Please verify manually. IC Number not found in QR code."

# Main route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['mc_file']
        print("File received:", file.filename)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            print("File saved to:", file_path)

            text = extract_text_from_image(file_path)
            ic_number = extract_ic_number(text)
            qr_data_list = extract_qr_data(file_path)

            if not ic_number:
                return render_template('index.html', result="❌ Could not extract IC Number.")

            if not qr_data_list:
                return render_template('index.html', result="❌ Could not detect any QR codes.")

            result = verify_ic_in_qr(qr_data_list, ic_number)
            return render_template('index.html', result=result)

    return render_template('index.html')

# Create upload directory and run the app
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
