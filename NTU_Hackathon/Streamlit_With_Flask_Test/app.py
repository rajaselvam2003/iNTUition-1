import os
import tempfile
import streamlit as st
from PyPDF2 import PdfFileReader


def read_pdf(file):
    with open(file, "rb") as f:
        pdf = PdfFileReader(f)
        pages = pdf.getNumPages()
        st.write(f"Number of pages: {pages}")


def main():
    st.set_page_config(page_title="PDF Viewer", page_icon="📄", layout="wide")

    st.title("PDF Viewer")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, uploaded_file.name)
            with open(filepath, "wb") as f:
                f.write(uploaded_file.read())
                st.success("File uploaded!")
                read_pdf(filepath)


if __name__ == "__main__":
    main()
