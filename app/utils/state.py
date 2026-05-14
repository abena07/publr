import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession        

from app.db.models import FailedFile, ProcessedFile
    

async def load_processed(user_id:uuid.UUID, session:AsyncSession):
    result = await session.execute(select(ProcessedFile).where(ProcessedFile.user_id == user_id))               
    return {row.gdrive_file_id for row in result.scalars().all()}
                     

async def save_processed(user_id:uuid.UUID, file_id:str, session:AsyncSession):
    session.add(ProcessedFile(user_id = user_id, gdrive_file_id=file_id))
    await session.commit()

async def load_failed(user_id:uuid.UUID, session:AsyncSession):
    result = await session.execute(select(FailedFile).where(FailedFile.user_id == user_id))
    return{row.gdrive_file_id: row.cloudinary_url for row in result.scalars().all()}


async def save_failed(user_id:uuid.UUID, file_id:str, cloudinary_url:str, session:AsyncSession):
    existing = await session.execute(
        select(FailedFile).where(FailedFile.user_id == user_id, FailedFile.gdrive_file_id == file_id)
    )
    if existing.scalar_one_or_none() is None:
        session.add(FailedFile(user_id=user_id, gdrive_file_id=file_id, cloudinary_url=cloudinary_url))
        await session.commit()

async def delete_failed(user_id: uuid.UUID, file_id: str, session: AsyncSession):
    await session.execute(
        delete(FailedFile).where(FailedFile.user_id == user_id, FailedFile.gdrive_file_id == file_id)
    )
    await session.commit()