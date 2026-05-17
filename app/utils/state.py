import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession        

from app.db.models import FailedFile, ProcessedFile
    

async def load_processed(user_id: uuid.UUID, session: AsyncSession):
    result = await session.execute(select(ProcessedFile).where(ProcessedFile.user_id == user_id))
    return {row.gdrive_file_id for row in result.scalars().all()}


async def load_processed_records(user_id: uuid.UUID, session: AsyncSession) -> dict:
    result = await session.execute(select(ProcessedFile).where(ProcessedFile.user_id == user_id))
    return {row.gdrive_file_id: row for row in result.scalars().all()}


async def save_processed(
    user_id: uuid.UUID,
    file_id: str,
    session: AsyncSession,
    cloudinary_public_id: str = None,
    instagram_media_id: str = None,
):
    session.add(ProcessedFile(
        user_id=user_id,
        gdrive_file_id=file_id,
        cloudinary_public_id=cloudinary_public_id,
        instagram_media_id=instagram_media_id,
    ))
    await session.commit()


async def set_instagram_media_id(user_id: uuid.UUID, file_id: str, media_id: str, session: AsyncSession):
    result = await session.execute(
        select(ProcessedFile).where(ProcessedFile.user_id == user_id, ProcessedFile.gdrive_file_id == file_id)
    )
    record = result.scalar_one_or_none()
    if record:
        record.instagram_media_id = media_id
        await session.commit()


async def delete_processed(user_id: uuid.UUID, file_id: str, session: AsyncSession):
    await session.execute(
        delete(ProcessedFile).where(ProcessedFile.user_id == user_id, ProcessedFile.gdrive_file_id == file_id)
    )
    await session.commit()

async def load_failed(user_id:uuid.UUID, session:AsyncSession):
    result = await session.execute(select(FailedFile).where(FailedFile.user_id == user_id))
    return{row.gdrive_file_id: row.cloudinary_url for row in result.scalars().all()}


async def save_failed(
    user_id: uuid.UUID,
    file_id: str,
    cloudinary_url: str,
    session: AsyncSession,
    cloudinary_public_id: str = None,
):
    existing = await session.execute(
        select(FailedFile).where(FailedFile.user_id == user_id, FailedFile.gdrive_file_id == file_id)
    )
    if existing.scalar_one_or_none() is None:
        session.add(FailedFile(
            user_id=user_id,
            gdrive_file_id=file_id,
            cloudinary_url=cloudinary_url,
            cloudinary_public_id=cloudinary_public_id,
        ))
        await session.commit()


async def get_failed_record(user_id: uuid.UUID, file_id: str, session: AsyncSession):
    result = await session.execute(
        select(FailedFile).where(FailedFile.user_id == user_id, FailedFile.gdrive_file_id == file_id)
    )
    return result.scalar_one_or_none()

async def delete_failed(user_id: uuid.UUID, file_id: str, session: AsyncSession):
    await session.execute(
        delete(FailedFile).where(FailedFile.user_id == user_id, FailedFile.gdrive_file_id == file_id)
    )
    await session.commit()