# import os
# import re
# import cv2
# import pytesseract
# import requests
# from bs4 import BeautifulSoup
# from flask import Flask, render_template, request
# from werkzeug.utils import secure_filename
# from pyzbar.pyzbar import decode

# # Configuration
# UPLOAD_FOLDER = 'uploaded_mcs'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

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

# # Helper: Extract Start Date (format: DD/MM/YYYY or DD-MM-YYYY)
# def extract_start_date(text):
#     match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', text)
#     return match.group(0) if match else None

# # Helper: Decode all QR codes
# def extract_qr_data(image_path):
#     image = cv2.imread(image_path)
#     decoded_objects = decode(image)
#     qr_data_list = [obj.data.decode('utf-8') for obj in decoded_objects]
#     print("Extracted QR Data:", qr_data_list)
#     return qr_data_list

# # Helper: Extract start date from QR string (format: DD/MM/YYYY or DD-MM-YYYY)
# def extract_start_date_from_qr(qr_data_list):
#     for qr_data in qr_data_list:
#         match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', qr_data)
#         if match:
#             return match.group(0)
#     return None

# # Helper: Check if IC and Start Date are consistent
# def verify_details(ic_number, qr_data_list, start_date, qr_start_date):
#     ic_verified = False
#     start_date_verified = False
#     for qr_data in qr_data_list:
#         if ic_number in qr_data:
#             ic_verified = True
#         if start_date and start_date in qr_data:
#             start_date_verified = True

#     results = []
#     results.append(f"1) ID on MC: {ic_number} | ID on QR: {'Found' if ic_verified else 'Not found'} {'✅' if ic_verified else '❌'}")
#     results.append(f"2) Start Date on MC: {start_date} | Start Date on QR: {qr_start_date or 'Not found'} {'✅' if start_date_verified else '❌'}")

#     if ic_verified and start_date_verified:
#         results.append("✅ MC is Legit!")
#     else:
#         results.append("⚠️ Please verify manually. Data mismatch found.")
    
#     return "<br>".join(results)

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
#             start_date = extract_start_date(text)
#             qr_data_list = extract_qr_data(file_path)
#             qr_start_date = extract_start_date_from_qr(qr_data_list)

#             if not ic_number:
#                 return render_template('index.html', result="❌ Could not extract IC Number.")
#             if not qr_data_list:
#                 return render_template('index.html', result="❌ Could not detect any QR codes.")

#             result = verify_details(ic_number, qr_data_list, start_date, qr_start_date)
#             return render_template('index.html', result=result)

#     return render_template('index.html')

# # Create upload directory and run the app
# if __name__ == '__main__':
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
#     app.run(debug=True)



















# import os
# import re
# import cv2
# import pytesseract
# import requests
# from bs4 import BeautifulSoup
# from flask import Flask, render_template, request
# from werkzeug.utils import secure_filename
# from pyzbar.pyzbar import decode

# # Configuration
# UPLOAD_FOLDER = 'uploaded_mcs'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Tesseract path (adjust for your OS if needed)
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# # Helpers
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def extract_text_from_image(image_path):
#     image = cv2.imread(image_path)
#     text = pytesseract.image_to_string(image)
#     print("Extracted OCR Text:", text)
#     return text

# def extract_ic_number(text):
#     match = re.search(r'T\d{7}[A-Z]', text)
#     return match.group(0) if match else None

# def extract_start_date(text):
#     # Match DD/MM/YYYY, DD-MM-YYYY, or DD-MMM-YYYY
#     match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4}|\d{2}-[A-Za-z]{3}-\d{4})', text)
#     return match.group(0) if match else None


# def extract_qr_urls(image_path):
#     image = cv2.imread(image_path)
#     decoded_objects = decode(image)
#     url_list = []

#     for obj in decoded_objects:
#         data = obj.data.decode('utf-8')
#         if data.startswith('http://') or data.startswith('https://'):
#             url_list.append(data)

#     print("Extracted QR URLs:", url_list)
#     return url_list

# def extract_details_from_qr_page(url):
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         text = response.text

#         ic_match = re.search(r'T\d{7}[A-Z]', text)
#         date_match = re.search(r'(\d{2}[/-]\d{2}[/-]\d{4})', text)

#         ic_number = ic_match.group(0) if ic_match else None
#         start_date = date_match.group(0) if date_match else None

#         print(f"From QR Page: IC = {ic_number}, Date = {start_date}")
#         return ic_number, start_date
#     except Exception as e:
#         print("Error fetching or parsing QR page:", e)
#         return None, None

# def verify_details(ic_ocr, ic_qr, date_ocr, date_qr):
#     ic_verified = (ic_ocr == ic_qr)
#     date_verified = (date_ocr == date_qr)

#     results = []
#     results.append(f"1) ID on MC: {ic_ocr} | ID on QR Page: {ic_qr or 'Not found'} {'✅' if ic_verified else '❌'}")
#     results.append(f"2) Start Date on MC: {date_ocr} | Start Date on QR Page: {date_qr or 'Not found'} {'✅' if date_verified else '❌'}")

#     if ic_verified and date_verified:
#         results.append("✅ MC is Legit!")
#     else:
#         results.append("⚠️ Please verify manually. Data mismatch found.")

#     return "<br>".join(results)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         file = request.files['mc_file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#             text = extract_text_from_image(file_path)
#             ic_ocr = extract_ic_number(text)
#             date_ocr = extract_start_date(text)

#             if not ic_ocr or not date_ocr:
#                 return render_template('index.html', result="❌ Could not extract IC or Start Date from image.")

#             qr_urls = extract_qr_urls(file_path)
#             if not qr_urls:
#                 return render_template('index.html', result="❌ No QR code URL found in image.")

#             ic_qr, date_qr = extract_details_from_qr_page(qr_urls[0])
#             result = verify_details(ic_ocr, ic_qr, date_ocr, date_qr)
#             return render_template('index.html', result=result)

#     return render_template('index.html')
    
# if __name__ == '__main__':
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
#     app.run(debug=True)







# import os
# import re
# import cv2
# import numpy as np
# import pytesseract
# from flask import Flask, render_template, request
# from werkzeug.utils import secure_filename
# from pyzbar.pyzbar import decode
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

# # Configuration
# UPLOAD_FOLDER = 'uploaded_mcs'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Tesseract path (adjust if needed)
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"  # change to your path

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def extract_text_from_image(image_path):
#     image = cv2.imread(image_path)
#     text = pytesseract.image_to_string(image)
#     print("Extracted OCR Text:", text)
#     return text

# def extract_ic_number(text):
#     match = re.search(r'T\d{7}[A-Z]', text)
#     return match.group(0) if match else None

# def extract_start_date(text):
#     # Supporting DD-MMM-YYYY and DD/MM/YYYY formats from your sample
#     match = re.search(r'(\d{2}[-/][A-Za-z]{3}[-/]\d{4}|\d{2}[/-]\d{2}[/-]\d{4})', text)
#     return match.group(0) if match else None

# def extract_qr_data(image_path):
#     image = cv2.imread(image_path)
#     decoded_objects = decode(image)
#     qr_data_list = [obj.data.decode('utf-8') for obj in decoded_objects]
#     print("Extracted QR Data:", qr_data_list)
#     return qr_data_list

# def ocr_full_page_from_url(url):
#     print("Opening URL in headless browser:", url)
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument("--window-size=1200,1800")
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     driver = webdriver.Chrome(options=chrome_options)
#     driver.get(url)
#     png = driver.get_screenshot_as_png()
#     driver.quit()

#     nparr = np.frombuffer(png, np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     text = pytesseract.image_to_string(img)
#     print("OCR Text from QR-linked page:", text)
#     return text

# def verify_details(ic_number, start_date, qr_ic, qr_start_date):
#     ic_verified = (ic_number == qr_ic)
#     start_date_verified = (start_date == qr_start_date)

#     results = []
#     results.append(f"1) ID on MC: {ic_number} | ID on QR Page: {qr_ic or 'Not found'} {'✅' if ic_verified else '❌'}")
#     results.append(f"2) Start Date on MC: {start_date} | Start Date on QR Page: {qr_start_date or 'Not found'} {'✅' if start_date_verified else '❌'}")

#     if ic_verified and start_date_verified:
#         results.append("✅ MC is Legit!")
#     else:
#         results.append("⚠️ Please verify manually. Data mismatch found.")
#     return "<br>".join(results)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         file = request.files['mc_file']
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#             # OCR from MC image
#             mc_text = extract_text_from_image(file_path)
#             ic_number = extract_ic_number(mc_text)
#             start_date = extract_start_date(mc_text)

#             # Extract QR code data URLs
#             qr_data_list = extract_qr_data(file_path)
#             if not ic_number or not start_date:
#                 return render_template('index.html', result="❌ Could not extract IC or Start Date from image.")
#             if not qr_data_list:
#                 return render_template('index.html', result="❌ Could not detect any QR codes.")

#             # Process each QR URL
#             for qr_url in qr_data_list:
#                 if qr_url.startswith("http"):
#                     try:
#                         qr_page_text = ocr_full_page_from_url(qr_url)
#                         qr_ic = extract_ic_number(qr_page_text)
#                         qr_start_date = extract_start_date(qr_page_text)
#                         result = verify_details(ic_number, start_date, qr_ic, qr_start_date)
#                         return render_template('index.html', result=result)
#                     except Exception as e:
#                         print("Error processing QR URL:", e)
#                         return render_template('index.html', result="❌ Error processing QR URL.")

#             return render_template('index.html', result="❌ No valid QR URLs found.")
#     return render_template('index.html')

# if __name__ == '__main__':
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
#     app.run(debug=True)




# import os
# import re
# import cv2
# import numpy as np
# import pytesseract
# import requests
# from flask import Flask, request, render_template
# from werkzeug.utils import secure_filename
# from pyzbar.pyzbar import decode
# from pdf2image import convert_from_path
# from io import BytesIO
# from PIL import Image

# app = Flask(__name__)
# UPLOAD_FOLDER = 'uploaded_mcs'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Set your Tesseract path here if needed (example for macOS)
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def extract_text_from_image(image):
#     # image is a cv2 image or PIL Image object
#     if isinstance(image, Image.Image):
#         # PIL image to OpenCV format
#         image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
#     text = pytesseract.image_to_string(image)
#     return text

# def extract_text_from_pdf(file_path):
#     # Convert first page of PDF to image
#     pages = convert_from_path(file_path, dpi=300, first_page=1, last_page=1)
#     if pages:
#         return pytesseract.image_to_string(pages[0])
#     return ""

# def extract_ic_number(text):
#     match = re.search(r'T\d{7}[A-Z]', text)
#     return match.group(0) if match else None

# def extract_start_date(text):
#     # Support formats like 25-Apr-2025 or 25/04/2025 or 25-04-2025
#     match = re.search(r'\b(\d{1,2}[-/][A-Za-z]{3}[-/]\d{4}|\d{2}[-/]\d{2}[-/]\d{4})\b', text)
#     return match.group(0) if match else None

# def extract_qr_data(image):
#     decoded_objects = decode(image)
#     return [obj.data.decode('utf-8') for obj in decoded_objects]

# def ocr_text_from_url(url):
#     try:
#         response = requests.get(url, timeout=5)
#         response.raise_for_status()
#         # OCR the whole page screenshot
#         # Since direct page screenshot is complicated, we OCR the raw HTML text as fallback
#         # Better is to get rendered screenshot (needs headless browser)
#         html_text = response.text
#         # Clean tags to plain text if needed
#         clean_text = re.sub('<[^<]+?>', ' ', html_text)
#         return clean_text
#     except Exception as e:
#         print(f"Error fetching OCR from URL: {e}")
#         return ""

# def verify_details(ic_mc, start_date_mc, ic_qr, start_date_qr):
#     ic_match = (ic_mc == ic_qr)
#     date_match = (start_date_mc == start_date_qr)
#     result = []
#     result.append(f"IC on MC: {ic_mc or 'Not found'}")
#     result.append(f"Start Date on MC: {start_date_mc or 'Not found'}")
#     result.append(f"IC from QR: {ic_qr or 'Not found'}")
#     result.append(f"Start Date from QR: {start_date_qr or 'Not found'}")
#     if ic_match and date_match:
#         result.append("✅ MC Verified Successfully!")
#     else:
#         result.append("⚠️ Data mismatch detected, please verify manually.")
#     return "\n".join(result)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         file = request.files.get('mc_file')
#         if not file or not allowed_file(file.filename):
#             return render_template('index.html', result="❌ Invalid file uploaded.")

#         filename = secure_filename(file.filename)
#         save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(save_path)

#         # Extract text and QR from image or PDF
#         ext = filename.rsplit('.', 1)[1].lower()
#         if ext == 'pdf':
#             mc_text = extract_text_from_pdf(save_path)
#             # For QR code from PDF, convert first page to image then decode
#             pages = convert_from_path(save_path, dpi=300, first_page=1, last_page=1)
#             qr_data_list = extract_qr_data(cv2.cvtColor(np.array(pages[0]), cv2.COLOR_RGB2BGR)) if pages else []
#         else:
#             img = cv2.imread(save_path)
#             mc_text = pytesseract.image_to_string(img)
#             qr_data_list = extract_qr_data(img)

#         ic_mc = extract_ic_number(mc_text)
#         start_date_mc = extract_start_date(mc_text)

#         if not qr_data_list:
#             return render_template('index.html', result="❌ No QR code detected.")

#         # We expect QR data to contain URL(s)
#         qr_url = None
#         for data in qr_data_list:
#             if data.startswith("http"):
#                 qr_url = data
#                 break

#         if not qr_url:
#             return render_template('index.html', result="❌ No valid QR URL found.")

#         qr_text = ocr_text_from_url(qr_url)
#         ic_qr = extract_ic_number(qr_text)
#         start_date_qr = extract_start_date(qr_text)

#         result = verify_details(ic_mc, start_date_mc, ic_qr, start_date_qr)
#         return render_template('index.html', result=result)

#     return render_template('index.html')

# if __name__ == '__main__':
#     if not os.path.exists(UPLOAD_FOLDER):
#         os.makedirs(UPLOAD_FOLDER)
#     app.run(debug=True)







# import os
# import tempfile
# from flask import Flask, request
# import pytesseract
# from PIL import Image
# import cv2
# import numpy as np
# from pyzbar.pyzbar import decode
# import requests
# from io import BytesIO
# from pdf2image import convert_from_path
# import re
# import bs4

# app = Flask(__name__)

# def extract_text_from_image(image):
#     return pytesseract.image_to_string(image)

# def extract_qr_data(image):
#     decoded_objs = decode(image)
#     qr_data = []
#     for obj in decoded_objs:
#         qr_data.append(obj.data.decode('utf-8'))
#     return qr_data

# def fetch_qr_page_text(url):
#     try:
#         r = requests.get(url)
#         r.raise_for_status()
#         # Extract visible text by stripping tags simply (naive)
#         soup = bs4.BeautifulSoup(r.text, 'html.parser')
#         text = soup.get_text(separator=' ')
#         return text
#     except Exception as e:
#         return ""

# def find_ic_and_start_date(text):
#     ic_pattern = r'\bT\d{7}[A-Z]\b'  # Example: T0508410A
#     start_date_pattern = r'(\d{1,2}[-/][A-Za-z]{3}[-/]\d{4})'  # Example: 25-Apr-2025

#     ic = None
#     start_date = None

#     ic_match = re.search(ic_pattern, text)
#     if ic_match:
#         ic = ic_match.group(0)

#     start_date_match = re.search(start_date_pattern, text)
#     if start_date_match:
#         start_date = start_date_match.group(0)

#     return ic, start_date

# def check_mark(val):
#     return "&#10004;" if val else "&#10060;"  # ✔ or ✘

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         file = request.files.get('file')
#         if not file:
#             return "<h3>No file uploaded</h3>"

#         filename = file.filename.lower()

#         # Convert file to PIL Image(s)
#         images = []
#         if filename.endswith(".pdf"):
#             # Save the uploaded PDF temporarily
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                 file.save(tmp.name)
#                 tmp_path = tmp.name
            
#             # Convert pdf to images (first page only)
#             pages = convert_from_path(tmp_path, dpi=300)
#             images = pages
            
#             # Clean up temp file
#             os.remove(tmp_path)
#         else:
#             image = Image.open(file.stream).convert("RGB")
#             images = [image]

#         # Extract OCR from first page/image
#         ocr_text = extract_text_from_image(images[0])

#         # Convert PIL image to cv2 image for QR decode
#         cv_image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
#         qr_codes = extract_qr_data(cv_image)

#         ic_mc, start_date_mc = find_ic_and_start_date(ocr_text)

#         ic_qr, start_date_qr = None, None
#         qr_text = ""
#         if qr_codes:
#             qr_url = qr_codes[0]
#             qr_text = fetch_qr_page_text(qr_url)
#             ic_qr, start_date_qr = find_ic_and_start_date(qr_text)

#         ic_match = (ic_mc == ic_qr) and (ic_mc is not None)
#         date_match = (start_date_mc == start_date_qr) and (start_date_mc is not None)

#         all_good = ic_match and date_match

#         # Build response HTML inline
#         return f"""
#         <html><body>
#         <h2>MC Verification Result</h2>
#         <p>IC on MC: {ic_mc} {check_mark(ic_match)}</p>
#         <p>Start Date on MC: {start_date_mc} {check_mark(date_match)}</p>
#         <p>IC from QR: {ic_qr if ic_qr else 'Not found'} {check_mark(ic_match)}</p>
#         <p>Start Date from QR: {start_date_qr if start_date_qr else 'Not found'} {check_mark(date_match)}</p>
#         <p>QR Codes found: {qr_codes if qr_codes else 'None'}</p>
#         <h3 style="color: {'green' if all_good else 'red'};">MC Verified Successfully! ✅</h3>
#         <hr>
#         <form method="POST" enctype="multipart/form-data">
#             <input type="file" name="file" accept=".jpg,.jpeg,.png,.pdf" required>
#             <input type="submit" value="Upload and Verify">
#         </form>
#         </body></html>
#         """

#     return """
#     <html><body>
#     <h2>Upload Medical Certificate (Image or PDF)</h2>
#     <form method="POST" enctype="multipart/form-data">
#         <input type="file" name="file" accept=".jpg,.jpeg,.png,.pdf" required>
#         <input type="submit" value="Upload and Verify">
#     </form>
#     </body></html>
#     """

# if __name__ == "__main__":
#     app.run(debug=True)





# import os
# import tempfile
# from flask import Flask, request
# import pytesseract
# from PIL import Image
# import cv2
# import numpy as np
# from pyzbar.pyzbar import decode
# import requests
# from io import BytesIO
# from pdf2image import convert_from_path
# import re
# import bs4

# app = Flask(__name__)

# def extract_text_from_image(image):
#     return pytesseract.image_to_string(image)

# def extract_qr_data(image):
#     decoded_objs = decode(image)
#     qr_data = []
#     for obj in decoded_objs:
#         qr_data.append(obj.data.decode('utf-8'))
#     return qr_data

# def fetch_qr_page_text(url):
#     try:
#         r = requests.get(url)
#         r.raise_for_status()
#         # Extract visible text by stripping tags simply (naive)
#         soup = bs4.BeautifulSoup(r.text, 'html.parser')
#         text = soup.get_text(separator=' ')
#         return text
#     except Exception as e:
#         return ""

# def find_ic_and_start_date(text):
#     ic_pattern = r'\bT\d{7}[A-Z]\b'  # Example: T0508410A
#     start_date_pattern = r'(\d{1,2}[-/][A-Za-z]{3}[-/]\d{4})'  # Example: 25-Apr-2025

#     ic = None
#     start_date = None

#     ic_match = re.search(ic_pattern, text)
#     if ic_match:
#         ic = ic_match.group(0)

#     start_date_match = re.search(start_date_pattern, text)
#     if start_date_match:
#         start_date = start_date_match.group(0)

#     return ic, start_date

# def check_mark(val):
#     return "&#10004;" if val else "&#10060;"  # ✔ or ✘

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         file = request.files.get('file')
#         if not file:
#             return "<h3>No file uploaded</h3>"

#         filename = file.filename.lower()

#         # Convert file to PIL Image(s)
#         images = []
#         if filename.endswith(".pdf"):
#             # Save the uploaded PDF temporarily
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                 file.save(tmp.name)
#                 tmp_path = tmp.name
            
#             # Convert pdf to images (first page only)
#             pages = convert_from_path(tmp_path, dpi=300)
#             images = pages
            
#             # Clean up temp file
#             os.remove(tmp_path)
#         else:
#             image = Image.open(file.stream).convert("RGB")
#             images = [image]

#         # Extract OCR from first page/image
#         ocr_text = extract_text_from_image(images[0])

#         # Convert PIL image to cv2 image for QR decode
#         cv_image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
#         qr_codes = extract_qr_data(cv_image)

#         ic_mc, start_date_mc = find_ic_and_start_date(ocr_text)

#         ic_qr, start_date_qr = None, None
#         qr_text = ""
#         if qr_codes:
#             qr_url = qr_codes[0]
#             qr_text = fetch_qr_page_text(qr_url)
#             ic_qr, start_date_qr = find_ic_and_start_date(qr_text)

#         ic_match = (ic_mc == ic_qr) and (ic_mc is not None)
#         date_match = (start_date_mc == start_date_qr) and (start_date_mc is not None)

#         all_good = ic_match and date_match

#         # Build response HTML inline
#         return f"""
#         <html><body>
#         <h2>MC Verification Result</h2>
#         <p>IC on MC: {ic_mc} {check_mark(ic_match)}</p>
#         <p>Start Date on MC: {start_date_mc} {check_mark(date_match)}</p>
#         <p>IC from QR: {ic_qr if ic_qr else 'Not found'} {check_mark(ic_match)}</p>
#         <p>Start Date from QR: {start_date_qr if start_date_qr else 'Not found'} {check_mark(date_match)}</p>
#         <p>QR Codes found: {qr_codes if qr_codes else 'None'}</p>
#         <h3 style="color: {'green' if all_good else 'red'};">MC Verified Successfully! ✅</h3>
#         <hr>
#         <form method="POST" enctype="multipart/form-data">
#             <input type="file" name="file" accept=".jpg,.jpeg,.png,.pdf" required>
#             <input type="submit" value="Upload and Verify">
#         </form>
#         </body></html>
#         """

#     return """
#     <html><body>
#     <h2>Upload Medical Certificate (Image or PDF)</h2>
#     <form method="POST" enctype="multipart/form-data">
#         <input type="file" name="file" accept=".jpg,.jpeg,.png,.pdf" required>
#         <input type="submit" value="Upload and Verify">
#     </form>
#     </body></html>
#     """

# if __name__ == "__main__":
#     app.run(debug=True)









import os
import tempfile
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests
import re
import bs4
from pdf2image import convert_from_path
import streamlit as st

# --- Your backend logic functions ---

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def extract_qr_data(image):
    decoded_objs = decode(image)
    qr_data = []
    for obj in decoded_objs:
        qr_data.append(obj.data.decode('utf-8'))
    return qr_data

def fetch_qr_page_text(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(separator=' ')
        return text
    except Exception as e:
        return ""

def find_ic_and_start_date(text):
    ic_pattern = r'\bT\d{7}[A-Z]\b'  # Example: T0508410A
    start_date_pattern = r'(\d{1,2}[-/][A-Za-z]{3}[-/]\d{4})'  # Example: 25-Apr-2025

    ic = None
    start_date = None

    ic_match = re.search(ic_pattern, text)
    if ic_match:
        ic = ic_match.group(0)

    start_date_match = re.search(start_date_pattern, text)
    if start_date_match:
        start_date = start_date_match.group(0)

    return ic, start_date

def check_mark(val):
    return "✔️" if val else "❌"

# --- Streamlit UI ---

st.title("🩺 Medical Certificate Verifier")

uploaded_file = st.file_uploader("Upload Medical Certificate (Image or PDF)", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file is not None:
    # Display uploaded image preview or PDF info
    if uploaded_file.type == "application/pdf":
        st.info("PDF uploaded — processing first page as image.")
    else:
        st.image(uploaded_file, caption="Uploaded Medical Certificate", use_column_width=True)
    
    if st.button("Verify MC"):
        with st.spinner("Processing..."):
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf" if uploaded_file.type=="application/pdf" else ".jpg") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name
            
            # Load images from file
            images = []
            if uploaded_file.type == "application/pdf":
                pages = convert_from_path(tmp_path, dpi=300)
                images = pages
            else:
                img = Image.open(tmp_path).convert("RGB")
                images = [img]
            
            # Remove temp file after loading
            os.remove(tmp_path)
            
            # Extract OCR from first image
            ocr_text = extract_text_from_image(images[0])
            st.subheader("Extracted Text from MC:")
            st.text_area("", ocr_text, height=300)
            
            # Convert PIL image to cv2 format for QR decoding
            cv_image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
            qr_codes = extract_qr_data(cv_image)
            
            ic_mc, start_date_mc = find_ic_and_start_date(ocr_text)
            
            ic_qr, start_date_qr = None, None
            qr_text = ""
            if qr_codes:
                qr_url = qr_codes[0]
                qr_text = fetch_qr_page_text(qr_url)
                ic_qr, start_date_qr = find_ic_and_start_date(qr_text)
            
            ic_match = (ic_mc == ic_qr) and (ic_mc is not None)
            date_match = (start_date_mc == start_date_qr) and (start_date_mc is not None)
            all_good = ic_match and date_match
            
            st.markdown("### Verification Results")
            st.write(f"**IC on MC:** {ic_mc} {check_mark(ic_match)}")
            st.write(f"**Start Date on MC:** {start_date_mc} {check_mark(date_match)}")
            st.write(f"**IC from QR:** {ic_qr if ic_qr else 'Not found'} {check_mark(ic_match)}")
            st.write(f"**Start Date from QR:** {start_date_qr if start_date_qr else 'Not found'} {check_mark(date_match)}")
            st.write(f"**QR Codes found:** {qr_codes if qr_codes else 'None'}")
            
            if all_good:
                st.success("✅ MC Verified Successfully!")
            else:
                st.error("❌ MC Verification Failed. Data mismatch detected.")
else:
    st.info("Please upload a Medical Certificate image or PDF to start verification.")

