# app.py

import streamlit as st
from pdf2image import convert_from_bytes
from tempfile import TemporaryDirectory
import io
import os
import sys
import pandas as pd

# Add utils path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Import the EasyOCR-based extraction function
from easyocr_extract import extract_table_easyocr

st.set_page_config(page_title="PDF Table Extractor (EasyOCR)", layout="centered")
st.title("📄 PDF Table Extractor with EasyOCR")

# --- OCR Language Selection ---
lang_map = {
    "English": "en",
    "Italian": "it",
    "German": "de",
    "French": "fr",
    "Spanish": "es",
    "Dutch": "nl"
}
selected_lang = st.selectbox("OCR Language", list(lang_map.keys()), index=0)
ocr_lang_code = lang_map[selected_lang]

# --- PDF Upload ---
uploaded_file = st.file_uploader("Upload a scanned PDF file", type=["pdf"])

if uploaded_file:
    with TemporaryDirectory() as temp_dir:
        st.info("Converting PDF to images...")
        images = convert_from_bytes(uploaded_file.read(), dpi=300, output_folder=temp_dir)
        st.success(f"✅ PDF converted: {len(images)} page(s) detected.")

        if st.checkbox("Show page previews"):
            for i, img in enumerate(images):
                st.image(img, caption=f"Page {i+1}", use_container_width=True)

        # --- Page Selection ---
        selected_pages = st.multiselect(
            "Select pages to extract (1-based)",
            options=list(range(1, len(images) + 1)),
            default=[]
        )

        all_dataframes = []

        for page_num in selected_pages:
            st.subheader(f"📄 Processing Page {page_num}")
            image = images[page_num - 1]

            with st.spinner(f"Running OCR on page {page_num}..."):
                df = extract_table_easyocr(image, lang=ocr_lang_code)

            st.success("✅ OCR completed")
            st.dataframe(df)
            all_dataframes.append((page_num, df))

        # --- Excel Export ---
        if all_dataframes:
            if st.button("📥 Download Excel File"):
                with io.BytesIO() as towrite:
                    with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                        for page_num, df in all_dataframes:
                            df.to_excel(writer, index=False, header=False, sheet_name=f"Page_{page_num}")
                    towrite.seek(0)
                    st.download_button(
                        label="Download Excel",
                        data=towrite,
                        file_name="extracted_tables.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
