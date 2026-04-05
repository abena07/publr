from datetime import datetime, timedelta, timezone
import os
import uuid
from typing import Annotated

from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.base import AsyncSessionLocal
from app.db.models import User

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 10800))


def create_access_token(user_id):
    payload ={
        "sub" : str(user_id),
        "exp" : datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]):
    user_id = decode_token(credentials.credentials)
    async with AsyncSessionLocal() as session:
        user = await session.get(User, uuid.UUID(user_id))
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user