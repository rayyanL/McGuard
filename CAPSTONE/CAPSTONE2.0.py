# Check using QR code URL
import os
import re
import pytesseract
import cv2
import pandas as pd
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pyzbar.pyzbar import decode
from urllib.parse import urlparse, parse_qs

UPLOAD_FOLDER = 'uploaded_mcs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(image_path):
    image = cv2.imread(image_path)
    text = pytesseract.image_to_string(image)
    print("Extracted Text:", text)  
    return text

def extract_ic_from_text(text):
    match = re.search(r'T\d{7}[A-Z]', text)
    return match.group(0) if match else None

def extract_qr_urls(image_path):
    image = cv2.imread(image_path)
    decoded_objects = decode(image)
    qr_urls = [obj.data.decode('utf-8') for obj in decoded_objects]
    print("Extracted QR URLs:", qr_urls)  
    return qr_urls

def extract_ic_from_qr_url(qr_url):
    parsed_url = urlparse(qr_url)
    query_params = parse_qs(parsed_url.query)
    ic_number = query_params.get('patient_nric', [None])[0]
    return ic_number

def verify_ic(ocr_ic, qr_ic):
    if not ocr_ic or not qr_ic:
        return "❌ Could not extract IC number properly."

    if ocr_ic == qr_ic:
        return "✅ MC is Legit!"
    else:
        return "⚠️ Please verify manually. Mismatch in IC number."

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
            ocr_ic = extract_ic_from_text(text)
            print("Extracted IC from OCR:", ocr_ic)

            qr_urls = extract_qr_urls(file_path)
            qr_ic = None

            for url in qr_urls:
                ic_from_qr = extract_ic_from_qr_url(url)
                if ic_from_qr:
                    qr_ic = ic_from_qr
                    print("Extracted IC from QR URL:", qr_ic)
                    break

            result = verify_ic(ocr_ic, qr_ic)
            return render_template('index.html', result=result)

    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
