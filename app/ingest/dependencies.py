import os
import uuid

from unstructured.partition.auto import partition
from unstructured.partition.csv import partition_csv
from unstructured.partition.doc import partition_doc
from unstructured.partition.docx import partition_docx
from unstructured.partition.text import partition_text

from app.ingest.config import TMP_FILES_DIR


class TmpFilesDir:
    def __init__(self) -> None:
        if not os.path.exists(TMP_FILES_DIR):
            os.mkdir(TMP_FILES_DIR)

    def write_file(self, filename, file_data):
        with open(f"{TMP_FILES_DIR}/{filename}", "wb") as f:
            f.write(file_data)

    def delete_file(self, filename):
        if not os.path.isfile(f"{TMP_FILES_DIR}/{filename}"):
            return

        os.remove(f"{TMP_FILES_DIR}/{filename}")


class Ingester:
    def create_partition(self, filename):
        file_type = os.path.splitext(filename)[-1].lower()
        file_path = f"{TMP_FILES_DIR}/{filename}"
        match file_type:
            case ".csv":
                return partition_csv(file_path)
            case ".doc":
                return partition_doc(file_path)
            case ".docx":
                return partition_docx(file_path)
            case ".txt":
                return partition_text(file_path)
            case _:
                return partition(file_path)


tmp_files_dir = TmpFilesDir()
ingester = Ingester()


async def get_tmp_files_dir():
    return tmp_files_dir


async def get_ingester():
    return ingester
