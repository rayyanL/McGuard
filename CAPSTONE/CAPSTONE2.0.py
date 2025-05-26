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
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- Session Initialization ---
if "verification_results" not in st.session_state:
    st.session_state.verification_results = []
if "verification_done" not in st.session_state:
    st.session_state.verification_done = False
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = "uploader_1"
if "dob_input_needed" not in st.session_state:
    st.session_state.dob_input_needed = False
if "dob_entered" not in st.session_state:
    st.session_state.dob_entered = ""

# --- Backend Logic ---
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'  

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def extract_qr_data(image):
    decoded_objs = decode(image)
    qr_data = [obj.data.decode('utf-8') for obj in decoded_objs]
    return qr_data

def fetch_qr_page_text(url, birthdate_ddmmyyyy=None):
    try:
        if birthdate_ddmmyyyy:
            url_with_birthdate = f"{url}?birthdate={birthdate_ddmmyyyy}"
            print(f"Fetching: {url_with_birthdate}")
            response = requests.get(url_with_birthdate, timeout=5)
        else:
            print(f"Fetching: {url}")
            response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        return f'Error fetching webpage: {str(e)}'

def find_ic_and_start_date(text):
    ic_pattern = r'\bT\d{7}[A-Z]\b'
    start_date_pattern = r'(\d{1,2}[-/][A-Za-z]{3}[-/]\d{4})'

    ic_match = re.search(ic_pattern, text)
    start_date_match = re.search(start_date_pattern, text)

    ic = ic_match.group(0) if ic_match else None
    start_date = start_date_match.group(0) if start_date_match else None

    return ic, start_date

def extract_name(text):
    ic_pattern = r'\bT\d{7}[A-Z]\b'
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for line in lines:
        match = re.search(ic_pattern, line)
        if match:
            ic = match.group(0)
            name = line.replace(ic, "").strip()
            return name

    return None

def check_mark(val):
    return "✔️" if val else "❌"

# --- Streamlit UI ---
st.title("🯪 Medical Certificate Verifier")

# 📅 Export Log
st.markdown("### 📁 Export Previous Verifications")
csv_path = os.path.join("logs", "verification_log.csv")
if os.path.exists(csv_path):
    with open(csv_path, "r") as f:
        csv_data = f.read()
    st.download_button("⬇️ Download Log CSV", data=csv_data, file_name="verification_log.csv", mime="text/csv")
else:
    st.info("No previous log file found yet.")

st.markdown("### 📄 Upload Medical Certificate (Image or PDF)")
uploaded_file = st.file_uploader("Upload MC File", type=["png", "jpg", "jpeg", "pdf"], key=st.session_state.uploader_key)

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        st.info("PDF uploaded — processing first page as image.")
    else:
        st.image(uploaded_file, caption="Uploaded Medical Certificate", use_container_width=True)

    if st.button("Verify MC"):
        with st.spinner("Processing..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf" if uploaded_file.type == "application/pdf" else ".jpg") as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            if uploaded_file.type == "application/pdf":
                images = convert_from_path(tmp_path, dpi=300)
            else:
                img = Image.open(tmp_path).convert("RGB")
                images = [img]

            os.remove(tmp_path)

            ocr_text = extract_text_from_image(images[0])
            st.subheader("Extracted Text from MC:")
            st.text_area("OCR Result", ocr_text, height=300)

            cv_image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
            qr_codes = extract_qr_data(cv_image)

            ic_mc, start_date_mc = find_ic_and_start_date(ocr_text)
            name_mc = extract_name(ocr_text)

            qr_url = qr_codes[0] if qr_codes else None

            if qr_url and "mc.gov.sg" in qr_url:
                st.session_state.dob_input_needed = True
                st.session_state.qr_url = qr_url
                st.warning("DOB required. Please select your date of birth below and submit to continue verification.")
            elif qr_url:
                qr_text = fetch_qr_page_text(qr_url)
                ic_qr, start_date_qr = find_ic_and_start_date(qr_text)
                st.session_state.ic_qr = ic_qr
                st.session_state.start_date_qr = start_date_qr
                st.session_state.qr_url = qr_url
            st.session_state.ocr_text = ocr_text
            st.session_state.ic_mc = ic_mc
            st.session_state.start_date_mc = start_date_mc
            st.session_state.name_mc = name_mc

if st.session_state.dob_input_needed:
    st.subheader("🔒 Date of Birth (DOB) Required to Proceed with Verification")
    st.markdown("Please select the MC holder date of birth (DOB) to unlock the verification page.")

    #show_calendar = st.checkbox("I want to enter DOB")
    #if show_calendar:
    dob_date = st.date_input(
        "Select the MC holder's Date of Birth (DOB) to continue with MC verification.",
        value=None,
        min_value=date(1970, 1, 1),
        max_value=date.today())
    if dob_date:
        st.caption(f"📅 DOB selected: {dob_date.strftime('%d/%m/%Y')}")

        if st.button("Submit DOB"):
            dob_str = dob_date.strftime("%d%m%Y")
            qr_text = fetch_qr_page_text(st.session_state.qr_url, birthdate_ddmmyyyy=dob_str)
            ic_qr, start_date_qr = find_ic_and_start_date(qr_text)
            st.session_state.ic_qr = ic_qr
            st.session_state.start_date_qr = start_date_qr
            st.session_state.dob_input_needed = False    

if "ic_qr" in st.session_state:
    ic_match = (st.session_state.ic_mc == st.session_state.ic_qr) and (st.session_state.ic_mc is not None)
    date_match = (st.session_state.start_date_mc == st.session_state.start_date_qr) and (st.session_state.start_date_mc is not None)
    all_good = ic_match and date_match

    st.markdown("### 🧪 Verification Results (Table Format)")
    st.markdown(f"""
    | Field                | From MC              | From QR Page              | Match |
    |---------------------|----------------------|---------------------------|-------|
    | **IC**              | {st.session_state.ic_mc or 'Not found'} | {st.session_state.ic_qr or 'Not found'}     | {check_mark(ic_match)} |
    | **Start Date**      | {st.session_state.start_date_mc or 'Not found'} | {st.session_state.start_date_qr or 'Not found'} | {check_mark(date_match)} |
    | **QR Code URL**     | \-                   | {st.session_state.qr_url or 'None'} | \- |
    """)

    if all_good:
        st.success("✅ MC Verified Successfully!")
    else:
        st.error("❌ MC Verification Failed. Data mismatch detected.")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = {
        "Verified At": timestamp,
        "ID": st.session_state.ic_mc or '',
        "Name": st.session_state.name_mc or '',
        "Start Date": st.session_state.start_date_mc or ''
    }

    st.session_state.verification_results.append(row)

    os.makedirs("logs", exist_ok=True)
    csv_path = os.path.join("logs", "verification_log.csv")
    write_header = not os.path.exists(csv_path)
    pd.DataFrame([row]).to_csv(csv_path, mode='a', header=write_header, index=False)

    st.session_state.verification_done = True

if st.session_state.verification_done:
    st.markdown("---")
    if st.button("🔄 Start Over"):
        st.session_state.verification_results = []
        st.session_state.clear()
        st.session_state.uploader_key = f"uploader_{np.random.randint(100000)}"
        st.rerun()
