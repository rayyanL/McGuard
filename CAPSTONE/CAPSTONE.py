# # Check using QR code information

# import os
# import re
# import pytesseract
# from flask import Flask, render_template, request
# from werkzeug.utils import secure_filename
# from pyzbar.pyzbar import decode
# import cv2

# UPLOAD_FOLDER = 'uploaded_mcs'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def extract_text_from_image(image_path):
#     image = cv2.imread(image_path)
#     text = pytesseract.image_to_string(image)
#     print("Extracted Text:", text)
#     return text

# def extract_ic_number(text):
#     match = re.search(r'T\d{7}[A-Z]', text)
#     return match.group(0) if match else None

# def extract_qr_data(image_path):
#     image = cv2.imread(image_path)
#     decoded_objects = decode(image)
#     qr_data_list = [obj.data.decode('utf-8') for obj in decoded_objects]
#     print("Extracted QR Data:", qr_data_list)
#     return qr_data_list

# def verify_ic_in_qr(qr_data_list, ic_number):
#     for qr_data in qr_data_list:
#         if ic_number in qr_data:
#             return "✅ MC is Legit!"
#     return "⚠️ Please verify manually. IC Number not found in QR code."

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

# if __name__ == '__main__':
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
#     app.run(debug=True)



# import numpy as np
# import os
# import re
# import cv2
# import requests
# import pytesseract
# import streamlit as st
# from pyzbar.pyzbar import decode
# from tempfile import NamedTemporaryFile
# from PIL import Image, ImageEnhance

# # Use Homebrew Tesseract (adjust path for Windows/Linux if needed)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # Helpers
# def preprocess_image(image_path):
#     # Open image using OpenCV
#     image = cv2.imread(image_path)
    
#     # Convert the image to grayscale
#     gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
#     # Apply contrast enhancement
#     pil_image = Image.fromarray(gray_image)
#     enhancer = ImageEnhance.Contrast(pil_image)
#     enhanced_image = enhancer.enhance(2)  # Increase contrast

#     # Convert back to OpenCV format
#     enhanced_image = cv2.cvtColor(np.array(enhanced_image), cv2.COLOR_RGB2BGR)
    
#     # Apply binary thresholding for better text recognition
#     _, thresh_image = cv2.threshold(enhanced_image, 150, 255, cv2.THRESH_BINARY)
    
#     return thresh_image

# def extract_text_from_image(image_path):
#     # Preprocess the image to improve OCR accuracy
#     preprocessed_image = preprocess_image(image_path)
    
#     # Run OCR with Tesseract
#     custom_config = r'--oem 3 --psm 6'  # For better text detection in a block
#     text = pytesseract.image_to_string(preprocessed_image, config=custom_config)
#     return text

# def extract_ic_number(text):
#     match = re.search(r'T\d{7}[A-Z]', text)
#     return match.group(0) if match else None

# def extract_mc_dates(text):
#     matches = re.findall(r'\d{2}/\d{2}/\d{4}', text)
#     return matches[:2] if len(matches) >= 2 else (None, None)

# def extract_qr_urls(image_path):
#     image = cv2.imread(image_path)
#     decoded_objects = decode(image)
#     qr_urls = [obj.data.decode('utf-8') for obj in decoded_objects]
#     return qr_urls

# def verify_with_url(qr_url, ic_number, start_date, end_date):
#     try:
#         response = requests.get(qr_url)
#         content = response.text
#         if all(value in content for value in [ic_number, start_date, end_date]):
#             return "✅ MC is Legit!"
#         else:
#             return "⚠️ Please verify manually. Mismatch in data."
#     except Exception as e:
#         return f"❌ Failed to fetch data from URL. Error: {e}"

# # Streamlit App
# st.title("Medical Certificate Verifier 🩺")
# uploaded_file = st.file_uploader("Upload your Medical Certificate (image only)", type=["png", "jpg", "jpeg"])

# if uploaded_file is not None:
#     st.image(uploaded_file, caption="Uploaded MC", use_column_width=True)
    
#     with NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
#         temp_file.write(uploaded_file.read())
#         temp_file_path = temp_file.name

#     if st.button("Check if it's Real or Fake"):
#         st.info("🔍 Processing MC...")

#         # Extract text from image
#         text = extract_text_from_image(temp_file_path)
#         st.text_area("📄 Extracted Text", text, height=300)

        
#         if not text.strip():  # Check if OCR returned any text
#             st.error("❌ No text found in the image. Please check the file quality.")
#         else:
#             # Extract IC number, dates, and QR URLs
#             ic_number = extract_ic_number(text)
#             start_date, end_date = extract_mc_dates(text)
#             qr_urls = extract_qr_urls(temp_file_path)

#             qr_url = None
#             for url in qr_urls:
#                 if ic_number and ic_number in url:
#                     qr_url = url
#                     break

#             if not all([ic_number, start_date, end_date, qr_url]):
#                 st.error("❌ Could not extract all necessary info. Please check the file quality.")
#             else:
#                 result = verify_with_url(qr_url, ic_number, start_date, end_date)
#                 st.success(result)








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
