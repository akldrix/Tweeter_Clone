import uuid
from pathlib import Path
from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_201_CREATED

from app.database import get_async_session
from app.models import Media, User
from app.routes.users import get_current_user
from app.schemas.tweets import MediaResponse

router = APIRouter(prefix="/medias", tags=["medias"])

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"


@router.post("", response_model=MediaResponse, status_code=HTTP_201_CREATED)
async def media(
    file: Annotated[UploadFile, File()],
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    file_extensions = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}.{file_extensions}"

    save_path = UPLOAD_DIR / unique_filename

    web_path = f"/static/uploads/{unique_filename}"

    async with aiofiles.open(save_path, "wb") as f:
        await f.write(await file.read())

    new_media = Media(file_path=web_path)
    session.add(new_media)
    await session.commit()
    await session.refresh(new_media)

    return {"result": True, "media_id": new_media.id}
