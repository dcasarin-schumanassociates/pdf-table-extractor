import streamlit as st
from pdf2image import convert_from_bytes
from tempfile import TemporaryDirectory
import io
import sys
import os
import pandas as pd
import pytesseract

# Local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.preprocessing import preprocess_image
from utils.detection import detect_table_cells
from utils.ocr import extract_cells_to_dataframe
from utils.text_extract import try_pdf_text_extraction

# UI setup
st.set_page_config(page_title="PDF Table Extractor", layout="centered")
st.title("📄 Upload a Scanned or Digital PDF Table")

ocr_lang = st.selectbox("Select OCR language", ["eng", "ita", "deu", "fra", "spa", "nld"], index=0)
use_ocr = st.checkbox("Force OCR (disable if PDF contains selectable text)", value=True)
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    with TemporaryDirectory() as temp_dir:
        st.info("Reading PDF...")
        pdf_bytes = uploaded_file.read()

        if not use_ocr:
            st.info("Trying text-based table extraction...")
            tables_by_page = try_pdf_text_extraction(io.BytesIO(pdf_bytes))

            any_tables_found = False
            for i, page_tables in enumerate(tables_by_page):
                if page_tables:
                    any_tables_found = True
                    st.subheader(f"Page {i + 1} - Extracted Table")
                    for table in page_tables:
                        df = pd.DataFrame(table)
                        st.dataframe(df)

            if any_tables_found:
                st.success("✅ Text-based extraction complete.")
                st.stop()
            else:
                st.warning("⚠️ No text-based tables found. Falling back to OCR.")

        # OCR path
        st.info("Converting PDF to images...")
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
                pre_img = preprocess_image(images[page_num - 1])
                table_img, boxes = detect_table_cells(pre_img)
                st.image(table_img, caption="Detected Table Cells", use_container_width=True)
                st.write(f"🧩 Detected {len(boxes)} cell(s)")

                df = extract_cells_to_dataframe(pre_img, boxes, lang=ocr_lang)

                if df.empty:
                    st.warning("⚠️ No text extracted from this page.")
                else:
                    st.dataframe(df)
                    all_dataframes.append(df)

            if all_dataframes:
                if st.button("📥 Download All as Excel"):
                    with io.BytesIO() as towrite:
                        with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
                            for i, df in enumerate(all_dataframes):
                                df.to_excel(
                                    writer,
                                    index=False,
                                    header=False,
                                    sheet_name=f"Page_{selected_pages[i]}"
                                )
                        towrite.seek(0)
                        st.download_button(
                            label="Download Excel File",
                            data=towrite,
                            file_name="multi_page_tables.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
