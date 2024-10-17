import os

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


tmp_files_dir = TmpFilesDir()


async def get_tmp_files_dir():
    return tmp_files_dir
