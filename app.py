import streamlit as st
from pdf2image import convert_from_bytes
from tempfile import TemporaryDirectory
import io
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.text_extract import try_pdf_text_extraction
from utils.ocr import extract_cells_to_dataframe
from utils.lp_ocr import extract_table_with_layoutparser
from utils.doctr_ocr import extract_with_doctr  # NEW doctr integration

st.set_page_config(page_title="PDF Table Extractor", layout="centered")
st.title("📄 Upload a Scanned PDF to Extract Tables")

ocr_lang = st.selectbox("Select OCR language", ["eng", "ita", "deu", "fra", "spa", "nld"], index=0)
ocr_engine = st.radio("Select OCR engine", ["doctr", "layoutparser", "classic"], index=0)

uploaded_file = st.file_uploader("Upload a scanned or digital PDF file", type=["pdf"])

if uploaded_file:
    with TemporaryDirectory() as temp_dir:
        st.info("Converting PDF to images...")
        images = convert_from_bytes(uploaded_file.read(), dpi=300, output_folder=temp_dir)
        st.success(f"PDF converted: {len(images)} page(s) detected.")

        if st.checkbox("Show page previews"):
            for i, img in enumerate(images):
                st.image(img, caption=f"Page {i+1}", use_container_width=True)

        selected_pages = st.multiselect(
            "Select pages to extract (1-based)",
            options=list(range(1, len(images) + 1)),
            format_func=lambda x: f"Page {x}"
        )

        all_dataframes = []

        if not selected_pages:
            st.warning("Please select at least one page.")

        for page_num in selected_pages:
            st.subheader(f"Page {page_num}")
            image = images[page_num - 1]

            progress = st.progress(0, text="🔍 Processing...")

            try:
                if ocr_engine == "doctr":
                    df = extract_with_doctr(image)
                elif ocr_engine == "layoutparser":
                    df = extract_table_with_layoutparser(image, lang=ocr_lang)
                else:
                    from utils.preprocessing import preprocess_image
                    from utils.detection import detect_table_cells

                    pre_img = preprocess_image(image)
                    _, boxes = detect_table_cells(pre_img)
                    df = extract_cells_to_dataframe(pre_img, boxes, lang=ocr_lang)

                all_dataframes.append(df)
                st.dataframe(df)
                progress.progress(100, text="✅ Done")

            except Exception as e:
                st.error(f"❌ Error on Page {page_num}: {e}")
                progress.empty()

        if all_dataframes:
            if st.button("📥 Download All as Excel"):
                with io.BytesIO() as towrite:
                    with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                        for i, df in enumerate(all_dataframes):
                            df.to_excel(writer, index=False, header=False, sheet_name=f"Page_{selected_pages[i]}")
                    towrite.seek(0)
                    st.download_button(
                        label="Download Excel File",
                        data=towrite,
                        file_name="multi_page_tables.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
