from pydantic import BaseModel


class UploadFilesContext(BaseModel):
    context: str
