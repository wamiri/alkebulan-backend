from typing import Annotated

from fastapi import UploadFile
from fastapi.param_functions import File
from fastapi.params import Depends
from fastapi.routing import APIRouter

from app.ingest.dependencies import get_tmp_files_dir


router = APIRouter(prefix="/ingest", tags=["Ingest"])


@router.post("/files/")
async def upload_files(files: list[UploadFile]):
    tmp_files_dir = get_tmp_files_dir()

    filenames = list()
    for file in files:
        file_data = await file.read()
        tmp_files_dir.write_file(file.filename, file_data)
        tmp_files_dir.delete_file(file.filename)
        filenames.append(file.filename)

    return filenames
