import os

import streamlit as st

from unstructured_file_processor import run_pipeline

uploaded_files = st.file_uploader(
    label="Upload your tabular file i.e. CSV, TSV, XLS, XLSX",
    accept_multiple_files=True,
    type=["csv", "tsv", "xls", "xlsx"],
)

unstructured_file_formats = ["xls", "xlsx"]
get_file_extension = lambda filename: filename.split(".")[-1]


def delete_files_from_folder(folder="unstructured"):
    for file in os.listdir(folder):
        os.unlink(os.path.join(folder, file))


for uploaded_file in uploaded_files:
    bytes_data = uploaded_file.read()
    file_extension = get_file_extension(uploaded_file.name)

    if file_extension in unstructured_file_formats:
        with open(f"unstructured/{uploaded_file.name}", "wb") as f:
            f.write(bytes_data)
        run_pipeline()
        delete_files_from_folder()

    else:
        with open(f"upload/{uploaded_file.name}", "wb") as f:
            f.write(bytes_data)

    st.write(f"{uploaded_file.name} uploaded")
