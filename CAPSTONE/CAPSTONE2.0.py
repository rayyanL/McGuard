# Feature 3


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



# streamlit run CAPSTONE/CAPSTONE2.0.py
