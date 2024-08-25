from fastapi import APIRouter, Path, Depends, UploadFile
from uuid import UUID, uuid4
from src import auth
from typing import Annotated
from src import db
import os
from src.models import Response
import shutil
from fastapi.responses import FileResponse
from src import models

router = APIRouter()
data_dir = os.path.join(os.getcwd(), 'data')
os.makedirs(data_dir, exist_ok=True)

@router.get('/file/{id}')
async def get(id: UUID = Path(...)):
    # user = auth.decode_token(token)
    file_item: models.File | None = db.query_one('File', {'id': id})
    if file_item:
        return FileResponse(path=file_item.file_path, filename=file_item.file_name, media_type=file_item.file_type)
    else:
        return Response(status_code=404)

@router.post('/file')
async def post(token: Annotated[str, Depends(auth.oauth2_scheme)], files: list[UploadFile]):
    user = auth.get_identity(token)
    user_id = db.query_one('User', {"name": user}).id
    suc_arr = []
    os.makedirs(os.path.join(data_dir, user_id), exist_ok=True)
    for file in files:
        file_id = str(uuid4())[:8]
        file_path = os.path.join(data_dir, user_id, file_id + '.' + file.filename.split('.')[-1])
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        # file_item = File(file_type=file.filename.split('.')[-1], file_name=file.filename, publisher_id=user_id)
        item = {
                "file_type": file.content_type,
                "file_name": file.filename,
                "publisher_id": user_id,
                "file_path": file_path}
        db.insert(table_name='File', item=item)
        suc_arr.append(item)

    return Response(data=suc_arr)

@router.get('/file_list')
async def get(token: Annotated[str, Depends(auth.oauth2_scheme)]):
    return db.get_user_files(token=token)