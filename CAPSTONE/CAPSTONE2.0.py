import os
import tempfile
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from pdf2image import convert_from_path
import streamlit as st
import re
from datetime import datetime

# --- OCR and helper functions ---

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def extract_qr_data(image):
    decoded_objs = decode(image)
    return [obj.data.decode('utf-8') for obj in decoded_objs]

def find_ic_and_cert_and_start_date(text):
    clean_text = " ".join(text.split()).upper()
    ic_pattern = r'\bT\d{7}[A-Z]\b'
    cert_pattern = r'NO[:\s]+(\d{6,})'  # e.g. No: 3140713
    start_date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})'

    ic = re.search(ic_pattern, clean_text)
    cert = re.search(cert_pattern, clean_text)
    dates = re.findall(start_date_pattern, clean_text)

    ic_val = ic.group(0) if ic else None
    cert_val = cert.group(1) if cert else None
    start_date = dates[0] if dates else None

    return ic_val, cert_val, start_date

def check_mark(val):
    return "✔️" if val else "❌"

def normalize_date(date_str):
    if not date_str:
        return None
    for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            continue
    return None

# --- Streamlit UI ---

st.set_page_config(page_title="Medical Certificate Verifier", layout="wide")

# Inject custom CSS for colors & styles
st.markdown("""
<style>
.header-title {
    background: linear-gradient(90deg, #4a90e2, #50e3c2);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    font-weight: 700;
    font-size: 3rem;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin-bottom: 20px;
    user-select: none;
}
.step1 {
    color: #FF6F61;
    font-weight: 700;
    font-size: 1.8rem;
    margin-top: 1.5rem;
}
.step2 {
    color: #4A90E2;
    font-weight: 700;
    font-size: 1.8rem;
    margin-top: 1.5rem;
}
.step3 {
    color: #7ED321;
    font-weight: 700;
    font-size: 1.8rem;
    margin-top: 1.5rem;
}
.metric-label {
    color: #50E3C2 !important;
    font-weight: 600 !important;
}
.stInfo {
    background-color: #d0f0ff !important;
    border-left: 5px solid #4A90E2 !important;
    padding: 10px !important;
    border-radius: 5px !important;
}
.stSuccess {
    background-color: #d7f0d8 !important;
    border-left: 5px solid #7ED321 !important;
    padding: 10px !important;
    border-radius: 5px !important;
}
.stError {
    background-color: #fbdede !important;
    border-left: 5px solid #FF6F61 !important;
    padding: 10px !important;
    border-radius: 5px !important;
}
.stButton > button:hover {
    background-color: #50e3c2 !important;
    color: white !important;
    font-weight: 700;
    transition: background-color 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-title">🩺 Medical Certificate Verifier</div>', unsafe_allow_html=True)
st.markdown("---")

# Step 1 - Upload MC
st.markdown('<div class="step1">Step 1: Upload Medical Certificate</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Supported formats: PNG, JPG, JPEG, PDF",
    type=["png", "jpg", "jpeg", "pdf"],
    help="Upload the Medical Certificate document or image file here."
)

if uploaded_file:
    with st.spinner("Processing uploaded file..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf" if uploaded_file.type=="application/pdf" else ".jpg") as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        images = []
        if uploaded_file.type == "application/pdf":
            images = convert_from_path(tmp_path, dpi=300)
        else:
            images = [Image.open(tmp_path).convert("RGB")]

        os.remove(tmp_path)

        ocr_text = extract_text_from_image(images[0])

    with st.expander("🔍 Extracted Text from Medical Certificate (OCR Output)", expanded=True):
        st.text_area("", ocr_text, height=200)

    ic_mc, cert_mc, start_date_mc = find_ic_and_cert_and_start_date(ocr_text)

    cv_image = cv2.cvtColor(np.array(images[0]), cv2.COLOR_RGB2BGR)
    qr_codes = extract_qr_data(cv_image)
    mc_qr_codes = [code for code in qr_codes if "everdr.com" in code and "cert_no=" in code]

    qr_url = mc_qr_codes[0] if mc_qr_codes else None

    st.markdown("### Extracted Information")
    col1, col2, col3 = st.columns(3)
    col1.metric("Certificate Number", cert_mc or "Not found")
    col2.metric("NRIC", ic_mc or "Not found")
    col3.metric("Start Date", start_date_mc or "Not found")

    if qr_url:
        st.markdown("---")
        st.markdown('<div class="step2">Step 2: Verify Certificate on Official Site</div>', unsafe_allow_html=True)
        if st.button("🔗 Open MC Verification Page"):
            st.markdown(f"[Click here to open verification page in new tab]({qr_url})", unsafe_allow_html=True)
            st.info("Please click 'Verify' on the website manually. Then return here to continue.")

        st.markdown("---")
        st.markdown('<div class="step3">Step 3: Provide Verification Result</div>', unsafe_allow_html=True)

        verification_text = st.text_area("Paste verification text from website here")

        if verification_text:
            ic_ver, cert_ver, start_date_ver = find_ic_and_cert_and_start_date(verification_text)

            st.markdown("---")
            st.markdown("### Verification Results")
            col1, col2 = st.columns(2)
            col1.write("**Medical Certificate Data**")
            col1.write(f"- IC: {ic_mc or 'N/A'}")
            col1.write(f"- Certificate No: {cert_mc or 'N/A'}")
            col1.write(f"- Start Date: {start_date_mc or 'N/A'}")

            col2.write("**Verified Data**")
            col2.write(f"- IC: {ic_ver or 'N/A'}")
            col2.write(f"- Certificate No: {cert_ver or 'N/A'}")
            col2.write(f"- Start Date: {start_date_ver or 'N/A'}")

            ic_match = (ic_mc == ic_ver) and (ic_mc is not None) and (ic_ver is not None)
            cert_match = (cert_mc == cert_ver) and (cert_mc is not None) and (cert_ver is not None)

            start_date_mc_norm = normalize_date(start_date_mc)
            start_date_ver_norm = normalize_date(start_date_ver)
            date_match = (start_date_mc_norm == start_date_ver_norm) and (start_date_mc_norm is not None) and (start_date_ver_norm is not None)

            st.markdown("---")
            st.markdown("### Match Summary")
            if ic_match and cert_match and date_match:
                st.success("✅ Medical Certificate Verified Successfully!")
            else:
                st.error("❌ Verification Failed: Data mismatch or missing.")

            st.write(f"**IC Match:** {check_mark(ic_match)}")
            st.write(f"**Certificate Number Match:** {check_mark(cert_match)}")
            st.write(f"**Start Date Match:** {check_mark(date_match)}")

else:
    st.info("Please upload a Medical Certificate image or PDF to begin.")
