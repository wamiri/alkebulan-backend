import os

from dotenv import load_dotenv

from utils.unstructured_file_processor import run_pipeline

load_dotenv()

UNSTRUCTURED_FILE_FORMATS = [".xls", ".xlsx"]
DATA_DIR = os.getenv("DATA_DIR")
UNSTRUCTURED_DIR = os.getenv("UNSTRUCTURED_DIR")


def upload_file(bytes_data, file):
    filename, file_extension = os.path.splitext(file)

    if file_extension in UNSTRUCTURED_FILE_FORMATS:
        with open(f"{UNSTRUCTURED_DIR}/{file}", "wb") as f:
            f.write(bytes_data)
            run_pipeline()
            file_extension = ".json"
    else:
        with open(f"{DATA_DIR}/{file}", "wb") as f:
            f.write(bytes_data)

    return filename, file_extension
