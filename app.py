import streamlit as st
from pdf2image import convert_from_bytes
from tempfile import TemporaryDirectory
import pandas as pd
import sys
import os
import io

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.doctr_extract import extract_with_doctr

st.set_page_config(page_title="PDF Table Extractor", layout="centered")
st.title("📄 Intelligent PDF Table Extractor with Doctr")

# File upload
uploaded_file = st.file_uploader("Upload a scanned PDF file", type=["pdf"])

if uploaded_file:
    # Language selector (for future compatibility)
    ocr_lang = st.selectbox("OCR Language (for future Tesseract fallback)", ["eng", "ita", "deu", "fra", "spa", "nld"], index=0)

    with TemporaryDirectory() as temp_dir:
        st.info("Converting PDF to preview images...")
        images = convert_from_bytes(uploaded_file.read(), dpi=150, output_folder=temp_dir)
        st.success(f"{len(images)} page(s) loaded.")

        if st.checkbox("Show page previews"):
            for i, img in enumerate(images):
                st.image(img, caption=f"Page {i+1}", use_container_width=True)

        # Reset file read position for OCR
        uploaded_file.seek(0)

        # Page selection
        selected_pages = st.multiselect("Select pages to extract (1-based)", options=list(range(1, len(images)+1)), default=[])

        all_dfs = []

        for page_num in selected_pages:
            st.subheader(f"📄 Page {page_num}")
            progress = st.progress(0, text="Extracting with Doctr...")

            try:
                df = extract_with_doctr(uploaded_file, page_index=page_num - 1)
                st.dataframe(df)
                all_dfs.append((page_num, df))
            except Exception as e:
                st.error(f"❌ Error on Page {page_num}: {e}")

            progress.progress(100, text="Done")

        if all_dfs:
            if st.button("📥
