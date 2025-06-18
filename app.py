# app.py
import streamlit as st
from pdf2image import convert_from_bytes
from tempfile import TemporaryDirectory
import io
import sys
import os
import pandas as pd

# Add local utils folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.preprocessing import preprocess_image
from utils.detection import detect_table_cells
from utils.ocr import extract_cells_to_dataframe
from utils.lp_ocr import extract_table_with_layoutparser

st.set_page_config(page_title="PDF Table Extractor (Layout-Aware)", layout="centered")
st.title("📄 PDF Table Extractor with Layout Awareness")

ocr_lang = st.selectbox("Select OCR language", ["eng", "ita", "deu", "fra", "spa", "nld"], index=0)
ocr_engine = st.radio("Choose OCR engine", ["Layout-aware (LayoutParser)", "Classic (Tesseract only)"])

uploaded_file = st.file_uploader("Upload a scanned PDF file", type=["pdf"])

if uploaded_file:
    with TemporaryDirectory() as temp_dir:
        st.info("Converting PDF to images...")
        images = convert_from_bytes(uploaded_file.read(), dpi=300, output_folder=temp_dir)
        st.success(f"PDF converted: {len(images)} page(s) detected.")

        if st.checkbox("Show page previews"):
            for i, img in enumerate(images):
                st.image(img, caption=f"Page {i + 1}", use_container_width=True)

        selected_pages = st.multiselect(
            "Select pages to extract (1-based)", 
            options=list(range(1, len(images) + 1)), 
            default=[]
        )

        if not selected_pages:
            st.warning("Please select at least one page.")
        else:
            all_dataframes = []

            for page_num in selected_pages:
                st.subheader(f"Page {page_num}")
                with st.spinner("Processing page..."):
                    image = images[page_num - 1]

                    if ocr_engine == "Layout-aware (LayoutParser)":
                        df = extract_table_with_layoutparser(image, lang=ocr_lang)
                        table_img = image
                    else:
                        pre_img = preprocess_image(image)
                        table_img, boxes = detect_table_cells(pre_img)
                        df = extract_cells_to_dataframe(pre_img, boxes, lang=ocr_lang)

                st.image(table_img, caption="Detected Table Cells", use_container_width=True)
                st.write(f"🧩 Detected {len(df)} row(s)")

                if df.empty:
                    st.warning("⚠️ No table detected on this page.")
                else:
                    st.dataframe(df)
                    all_dataframes.append(df)

            if all_dataframes:
                if st.button("📥 Download All as Excel"):
                    with io.BytesIO() as towrite:
                        with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
                            for i, df in enumerate(all_dataframes):
                                df.to_excel(writer, index=False, header=False, sheet_name=f"Page_{selected_pages[i]}")
                        towrite.seek(0)
                        st.download_button(
                            label="Download Excel File",
                            data=towrite,
                            file_name="tables_extracted.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
