import secrets
import uuid
from typing import Optional

from app.db.base import AsyncSessionLocal
from app.db.models import OAuthState


async def create_login_nonce() -> str:
    token = secrets.token_urlsafe(32)
    async with AsyncSessionLocal() as session:
        session.add(OAuthState(token=token))
        await session.commit()
    return token


async def consume_login_nonce(nonce: str) -> bool:
    async with AsyncSessionLocal() as session:
        row = await session.get(OAuthState, nonce)
        if row is None or row.user_id is not None:
            return False
        await session.delete(row)
        await session.commit()
    return True


async def create_state(user_id: uuid.UUID) -> str:
    token = secrets.token_urlsafe(32)
    async with AsyncSessionLocal() as session:
        session.add(OAuthState(token=token, user_id=user_id))
        await session.commit()
    return token


async def consume_state(state: str) -> Optional[uuid.UUID]:
    async with AsyncSessionLocal() as session:
        row = await session.get(OAuthState, state)
        if row is None:
            return None
        user_id = row.user_id
        await session.delete(row)
        await session.commit()
    return user_id
