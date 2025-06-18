import streamlit as st
from pdf2image import convert_from_bytes
from tempfile import TemporaryDirectory
import io
import os
import sys
import pandas as pd

# Add utils folder to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Import EasyOCR extractor
from easyocr_extract import extract_table_easyocr

# Streamlit app config
st.set_page_config(page_title="🧠 PDF Table Extractor (EasyOCR)", layout="centered")
st.title("📄 Extract Tables from Scanned PDFs with EasyOCR")

# Upload input
uploaded_file = st.file_uploader("Upload a scanned PDF file", type=["pdf"])

if uploaded_file:
    with TemporaryDirectory() as temp_dir:
        st.info("Converting PDF pages to images...")
        images = convert_from_bytes(uploaded_file.read(), dpi=300, output_folder=temp_dir)
        st.success(f"✅ PDF converted: {len(images)} page(s) detected.")

        if st.checkbox("Show page previews"):
            for i, img in enumerate(images):
                st.image(img, caption=f"Page {i+1}", use_container_width=True)

        selected_pages = st.multiselect(
            "Select pages to extract (1-based index)", 
            options=list(range(1, len(images)+1)), 
            default=[]
        )

        all_dataframes = []

        for page_num in selected_pages:
            st.subheader(f"🔎 Processing Page {page_num}")
            image = images[page_num - 1]

            with st.spinner(f"Running EasyOCR on page {page_num}..."):
                df = extract_table_easyocr(image)

            st.success("✅ OCR complete")
            st.dataframe(df)
            all_dataframes.append((page_num, df))

        if all_dataframes:
            if st.button("📥 Download All Tables as Excel"):
                with io.BytesIO() as towrite:
                    with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                        for page_num, df in all_dataframes:
                            df.to_excel(writer, index=False, header=False, sheet_name=f"Page_{page_num}")
                    towrite.seek(0)
                    st.download_button(
                        label="Download Excel File",
                        data=towrite,
                        file_name="extracted_tables_easyocr.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
