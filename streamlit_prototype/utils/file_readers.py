import os

from dotenv import load_dotenv
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import (CSVReader, DocxReader, EpubReader,
                                      FlatReader, PDFReader)
from llama_index.readers.json import JSONReader

load_dotenv()
DATA_DIR = "data"

file_readers = {
    ".csv": CSVReader(),
    ".tsv": CSVReader(),
    ".docx": DocxReader(),
    ".pdf": PDFReader(),
    ".epub": EpubReader(),
    ".json": JSONReader(),
    ".txt": FlatReader(),
}


def read_file(filename, file_extension):
    parser = file_readers.get(file_extension)
    if parser is None:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    file_extractor = {file_extension: parser}
    documents = SimpleDirectoryReader(
        input_files=[f"{DATA_DIR}/{filename}{file_extension}"],
        file_extractor=file_extractor,
    ).load_data()

    return documents
