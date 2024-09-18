import os

from dotenv import load_dotenv

from utils.unstructured_file_processor import run_pipeline

load_dotenv()
UNSTRUCTURED_FILE_FORMATS = [".xls", ".xlsx"]
DATA_DIR = "data"
UNSTRUCTURED_DIR = "unstructured"


def upload_file(bytes_data, file):
    filename, file_extension = os.path.splitext(file)

    if file_extension in UNSTRUCTURED_FILE_FORMATS:
        with open(f"{UNSTRUCTURED_DIR}/{file}", "wb") as f:
            f.write(bytes_data)
        run_pipeline()
        filename += file_extension
        file_extension = ".json"
    else:
        with open(f"{DATA_DIR}/{file}", "wb") as f:
            f.write(bytes_data)

    return filename, file_extension
