from typing import Annotated

from fastapi import UploadFile
from fastapi.param_functions import File
from fastapi.routing import APIRouter

router = APIRouter(prefix="/ingest", tags=["Ingest"])


@router.route("/upload-files")
async def upload_files(
    files: Annotated[list[UploadFile], File()],
):
    return {"filenames": [file.filename for file in files]}
