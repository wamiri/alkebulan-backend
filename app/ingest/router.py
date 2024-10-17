from typing import Annotated

from fastapi import UploadFile
from fastapi.params import Depends
from fastapi.routing import APIRouter

from app.ingest.dependencies import (
    Ingester,
    TmpFilesDir,
    get_ingester,
    get_tmp_files_dir,
)
from app.users.dependencies import get_current_user
from app.users.models import UserData

router = APIRouter(prefix="/ingest", tags=["Ingest"])


@router.post("/files/")
async def upload_files(
    files: list[UploadFile],
    current_user: Annotated[UserData, Depends(get_current_user)],
    tmp_files_dir: Annotated[TmpFilesDir, Depends(get_tmp_files_dir)],
    ingester: Annotated[Ingester, Depends(get_ingester)],
):
    filenames = dict()
    for file in files:
        file_data = await file.read()
        tmp_files_dir.write_file(file.filename, file_data)
        filenames[file.filename] = 0

    for filename in filenames:
        documents = ingester.create_partition(filename)
        filenames[filename] = len(documents)
        tmp_files_dir.delete_file(filename)

    return filenames
