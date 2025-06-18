# app.py

import streamlit as st
from pdf2image import convert_from_bytes
from tempfile import TemporaryDirectory
import io
import sys
import os
import pandas as pd

# Add local utils path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Local modules
from utils.preprocessing import preprocess_image
from utils.detection import detect_table_cells
from utils.ocr import extract_cells_to_dataframe
from utils.text_extract import try_pdf_text_extraction
from utils.lp_ocr import extract_table_with_layoutparser

# Streamlit UI setup
st.set_page_config(page_title="PDF Table Extractor", layout="centered")
st.title("📄 PDF Table Extractor")

ocr_lang = st.selectbox("Select OCR language", ["eng", "ita", "deu", "fra", "spa", "nld"], index=0)

engine = st.radio(
    "Choose table extraction method:",
    ["PDF Table Extraction (lattice)", "Layout-aware OCR (LayoutParser)", "Classic OCR (Tesseract + OpenCV)"]
)

uploaded_file = st.file_uploader("Upload a scanned or digital PDF file", type=["pdf"])

if uploaded_file:
    with TemporaryDirectory() as temp_dir:
        st.info("Reading PDF and converting to images...")
        pdf_bytes = uploaded_file.read()
        images = convert_from_bytes(pdf_bytes, dpi=300, output_folder=temp_dir)
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
                image = images[page_num - 1]

                with st.spinner("Processing page..."):
                    df = pd.DataFrame()

                    if engine == "PDF Table Extraction (lattice)":
                        st.write("🔎 Trying PDF structure-based table extraction (lattice mode)...")
                        tables = try_pdf_text_extraction(io.BytesIO(pdf_bytes))
                        page_tables = tables[page_num - 1] if len(tables) >= page_num else []

                        if page_tables:
                            df = pd.DataFrame(page_tables[0])
                            st.success("✅ Table detected using lattice mode.")
                        else:
                            st.warning("⚠️ No tables found using lattice parsing.")

                    elif engine == "Layout-aware OCR (LayoutParser)":
                        df = extract_table_with_layoutparser(image, lang=ocr_lang)

                    elif engine == "Classic OCR (Tesseract + OpenCV)":
                        pre_img = preprocess_image(image)
                        table_img, boxes = detect_table_cells(pre_img)
                        df = extract_cells_to_dataframe(pre_img, boxes, lang=ocr_lang)
                        st.image(table_img, caption="Detected Table Cells", use_container_width=True)

                if df.empty:
                    st.warning("⚠️ No table extracted on this page.")
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

