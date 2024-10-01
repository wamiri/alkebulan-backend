import hashlib
import os
import uuid

import unstructured_client
from img2table.document import PDF
from img2table.ocr import TesseractOCR
from langchain_core.documents import Document
from unstructured.chunking.title import chunk_by_title
from unstructured.partition.auto import partition
from unstructured.partition.doc import partition_doc
from unstructured.partition.docx import partition_docx
from unstructured.partition.image import partition_image
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.text import partition_text
from unstructured_client.models import operations, shared


class Ingest:
    def __init__(self, open_ai_api_key, open_ai_server_url):
        self.client = unstructured_client.UnstructuredClient(
            api_key_auth=open_ai_api_key,
            server_url=open_ai_server_url,
        )

    def createPartition(self, file_path, file_type):
        extension = os.path.splitext(file_path)[-1].lower()
        file_elements = self.createPartitionByFileType(file_path, extension)
        file_dict = [el.to_dict() for el in file_elements]
        return file_dict

    def createPartitionByFileType(self, file_path, file_type):
        match file_type:
            case ".pdf":
                return partition_pdf(file_path)
            case ".doc":
                return partition_doc(file_path)
            case ".docx":
                return partition_docx(file_path)
            case ".jpeg" | ".png" | ".jpeg":
                return self.createImagePartition(file_path, False)
            case ".txt":
                return partition_text(file_path)
            case _:
                return partition(file_path)

    def createImagePartition(file_path, isOcrEnabled):
        if isOcrEnabled:
            return partition_image(file_path, strategy="ocr_only")
        else:
            return partition_image(file_path)

    def normalizePDF(document_dict, partition_labels, chapter):
        label_ids = {}
        for element in document_dict:
            for label in partition_labels:
                if element["text"] == label and element["type"] == "Title":
                    label_ids[element["element_id"]] = chapter
                    break
        return label_ids

    def extract_tables(pdf_path):
        ocr = TesseractOCR(n_threads=1, lang="eng")
        pdf = PDF(src=pdf_path)

        # Extract tables
        extracted_tables = pdf.extract_tables(
            ocr=ocr, implicit_rows=True, borderless_tables=True, min_confidence=70
        )

        return extracted_tables

    def extractPDFWithId(pdf_path):
        pdf_doc = partition_pdf(pdf_path)

        # Prepare to store the modified text with table placeholders
        modified_text = ""
        table_identifiers = []

        # Extract content while placing unique IDs where tables are found
        for element in pdf_doc.elements:
            if element.type == "table":  # Assuming Unstructured identifies tables
                table_id = str(uuid.uuid4())  # Generate a unique table ID
                modified_text += f"[Table Placeholder: {table_id}]\n"
                table_identifiers.append(table_id)
            else:
                modified_text += element.text + "\n"

        # Return the modified text with placeholders and the table identifiers
        return modified_text, table_identifiers

    def extract_tables_with_id(pdf_path, table_identifiers):
        # Load the PDF with img2table
        ocr = TesseractOCR(n_threads=1, lang="eng")
        pdf = PDF(src=pdf_path)

        # Extract tables using img2table and link them with the placeholders
        tables = pdf.extract_tables(
            ocr=ocr, implicit_rows=True, borderless_tables=True, min_confidence=70
        )

        # Create a list of extracted tables with their respective IDs
        extracted_tables = []
        for index, table in enumerate(tables):
            table_id = table_identifiers[
                index
            ]  # Use the corresponding unique ID from Step 1
            extracted_tables.append({"table_id": table_id, "table_data": table})

    def extractTextFromPDF(self, pdf_path):
        with open(pdf_path, "rb") as f:
            data = f.read()

        req = operations.PartitionRequest(
            partition_parameters=shared.PartitionParameters(
                files=shared.Files(
                    content=data,
                    file_name=pdf_path,
                ),
                # --- Other partition parameters ---
                # Note: Defining 'strategy', 'chunking_strategy', and 'output_format'
                # parameters as strings is accepted, but will not pass strict type checking. It is
                # advised to use the defined enum classes as shown below.
                strategy=shared.Strategy.AUTO,
                languages=["eng"],
            ),
        )

        response = self.client.general.partition(request=req)
        return response

    def replaceTableWithTableId(response):
        text_with_placeholders = ""
        table_mapping = {}
        table_identifiers = []
        for element in response.elements:
            if element["type"] == "Table":
                table_id = str(uuid.uuid4())
                placeholder = f"[TABLE Placeholder: {table_id}]\n"
                text_with_placeholders += placeholder
                table_mapping[table_id] = element
                table_identifiers.append(table_id)
            else:
                text_with_placeholders += element["text"] + "\n"

        return text_with_placeholders, table_mapping, table_identifiers


class Chunk:
    def createChunk(file_element):
        chunks = chunk_by_title(
            file_element,
            combine_text_under_n_chars=100,
            max_characters=3000,
        )
        return chunks

    def createHash(id):
        return hashlib.sha256().update((id).encode("utf-8")).hexdigest()

    # Add metadata to chunks
    def processChunk(self, chunks):
        documents = []
        for element in chunks:
            metadata = element.metadata.to_dict()
            metadata["source"] = metadata["filename"]
            metadata["hash_id"] = self.createHash(element.id)
            documents.append(Document(page_content=element.text, metadata=metadata))
        return documents
