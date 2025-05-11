# import os
# import re
# import cv2
# import pytesseract
# from flask import Flask, render_template, request
# from werkzeug.utils import secure_filename
# from pyzbar.pyzbar import decode

# # Configuration
# UPLOAD_FOLDER = 'uploaded_mcs'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','pdf'}

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Tesseract path for macOS (adjust if needed)
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# # Helper: Check file extension
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# # Helper: OCR text extraction
# def extract_text_from_image(image_path):
#     image = cv2.imread(image_path)
#     text = pytesseract.image_to_string(image)
#     print("Extracted Text:", text)
#     return text

# # Helper: Extract IC number (e.g. T0721279D)
# def extract_ic_number(text):
#     match = re.search(r'T\d{7}[A-Z]', text)
#     return match.group(0) if match else None

# # Helper: Decode all QR codes
# def extract_qr_data(image_path):
#     image = cv2.imread(image_path)
#     decoded_objects = decode(image)
#     qr_data_list = [obj.data.decode('utf-8') for obj in decoded_objects]
#     print("Extracted QR Data:", qr_data_list)
#     return qr_data_list

# # Helper: Check if IC number is in any QR data string
# def verify_ic_in_qr(qr_data_list, ic_number):
#     for qr_data in qr_data_list:
#         if ic_number in qr_data:
#             return "✅ MC is Legit!"
#     return "⚠️ Please verify manually. IC Number not found in QR code."

# # Main route
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         file = request.files['mc_file']
#         print("File received:", file.filename)

#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)
#             print("File saved to:", file_path)

#             text = extract_text_from_image(file_path)
#             ic_number = extract_ic_number(text)
#             qr_data_list = extract_qr_data(file_path)

#             if not ic_number:
#                 return render_template('index.html', result="❌ Could not extract IC Number.")

#             if not qr_data_list:
#                 return render_template('index.html', result="❌ Could not detect any QR codes.")

#             result = verify_ic_in_qr(qr_data_list, ic_number)
#             return render_template('index.html', result=result)

#     return render_template('index.html')

# # Create upload directory and run the app
# if __name__ == '__main__':
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
#     app.run(debug=True)




################support new format#############
########## scan ocr and qr code for IC and Start Date########
######## 
import os
import re
import cv2
import pytesseract
import numpy as np
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path  # For handling PDF files

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

# Helper: OCR text extraction (supports PDF and images)
def extract_text_from_image(image_path):
    if image_path.lower().endswith('.pdf'):
        images = convert_from_path(image_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        print("Extracted Text from PDF:", text)
        return text
    else:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Unable to read image: {image_path}")
        text = pytesseract.image_to_string(image)
        print("Extracted Text:", text)
        return text

# Helper: Extract IC number (e.g. T0721279D)
def extract_ic_number(text):
    match = re.search(r'T\d{7}[A-Z]', text)
    return match.group(0) if match else None

# Helper: Decode all QR codes (only supports image files)
def extract_qr_data(image_path):
    if image_path.lower().endswith('.pdf'):
        images = convert_from_path(image_path)
        all_qr_data = []
        for image in images:
            # Convert PIL image to OpenCV format
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            decoded_objects = decode(image_cv)
            all_qr_data.extend([obj.data.decode('utf-8') for obj in decoded_objects])
        print("Extracted QR Data from PDF:", all_qr_data)
        return all_qr_data
    else:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Unable to read image for QR decoding: {image_path}")
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

            try:
                text = extract_text_from_image(file_path)
                ic_number = extract_ic_number(text)
                qr_data_list = extract_qr_data(file_path)

                if not ic_number:
                    return render_template('index.html', result="❌ Could not extract IC Number.")

                if not qr_data_list:
                    return render_template('index.html', result="❌ Could not detect any QR codes.")

                result = verify_ic_in_qr(qr_data_list, ic_number)
                return render_template('index.html', result=result)

            except Exception as e:
                print("Error:", e)
                return render_template('index.html', result=f"❌ Error: {str(e)}")

    return render_template('index.html')

# Create upload directory and run the app
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
