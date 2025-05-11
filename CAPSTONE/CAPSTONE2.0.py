import os
import re
import cv2
import pytesseract
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pyzbar.pyzbar import decode

# Configuration
UPLOAD_FOLDER = 'uploaded_mcs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

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

# Helper: Extract Start Date (format: DD/MM/YYYY or DD-MM-YYYY)
def extract_start_date(text):
    match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', text)
    return match.group(0) if match else None

# Helper: Decode all QR codes
def extract_qr_data(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    qr_data_list = [obj.data.decode('utf-8') for obj in decoded_objects]
    print("Extracted QR Data:", qr_data_list)
    return qr_data_list

# Helper: Extract start date from QR string (format: DD/MM/YYYY or DD-MM-YYYY)
def extract_start_date_from_qr(qr_data_list):
    for qr_data in qr_data_list:
        match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', qr_data)
        if match:
            return match.group(0)
    return None

# Helper: Check if IC and Start Date are consistent
def verify_details(ic_number, qr_data_list, start_date, qr_start_date):
    ic_verified = False
    start_date_verified = False
    for qr_data in qr_data_list:
        if ic_number in qr_data:
            ic_verified = True
        if start_date and start_date in qr_data:
            start_date_verified = True

    results = []
    results.append(f"1) ID on MC: {ic_number} | ID on QR: {'Found' if ic_verified else 'Not found'} {'✅' if ic_verified else '❌'}")
    results.append(f"2) Start Date on MC: {start_date} | Start Date on QR: {qr_start_date or 'Not found'} {'✅' if start_date_verified else '❌'}")

    if ic_verified and start_date_verified:
        results.append("✅ MC is Legit!")
    else:
        results.append("⚠️ Please verify manually. Data mismatch found.")
    
    return "<br>".join(results)

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
            start_date = extract_start_date(text)
            qr_data_list = extract_qr_data(file_path)
            qr_start_date = extract_start_date_from_qr(qr_data_list)

            if not ic_number:
                return render_template('index.html', result="❌ Could not extract IC Number.")
            if not qr_data_list:
                return render_template('index.html', result="❌ Could not detect any QR codes.")

            result = verify_details(ic_number, qr_data_list, start_date, qr_start_date)
            return render_template('index.html', result=result)

    return render_template('index.html')

# Create upload directory and run the app
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
