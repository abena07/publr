from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select

from app.db.base import AsyncSessionLocal
from app.db.models import WaitlistEntry

router = APIRouter(tags=["waitlist"])

BETA_SPOTS = 25


class WaitlistRequest(BaseModel):
    google_email: str
    facebook_name: str


@router.post("/api/waitlist")
async def join_waitlist(body: WaitlistRequest):
    async with AsyncSessionLocal() as session:
        count_result = await session.execute(select(func.count()).select_from(WaitlistEntry))
        count = count_result.scalar()

        entry = WaitlistEntry(google_email=body.google_email, facebook_name=body.facebook_name)
        session.add(entry)
        await session.commit()

        position = count + 1
        return {"position": position, "in_beta": position <= BETA_SPOTS}


@router.get("/api/waitlist/count")
async def waitlist_count():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count()).select_from(WaitlistEntry))
        count = result.scalar()
        return {"count": count, "remaining": max(0, BETA_SPOTS - count)}
