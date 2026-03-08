import asyncio
import os
import httpx

BASE = "https://graph.facebook.com/v21.0"


async def publish_to_instagram(image_url: str, caption: str = "") -> bool:
    user_id = os.environ["INSTAGRAM_USER_ID"]
    token = os.environ["INSTAGRAM_ACCESS_TOKEN"]

    async with httpx.AsyncClient() as client:
        # Step 1 — create container
        r = await client.post(
            f"{BASE}/{user_id}/media",
            params={
                "image_url": image_url,
                "caption": caption,
                "access_token": token,
            }
        )
        if r.is_error:
            raise Exception(f"Instagram container error: {r.json()}")
        creation_id = r.json()["id"]

        # Step 2 — wait for FINISHED
        for _ in range(10):
            s = await client.get(
                f"{BASE}/{creation_id}",
                params={
                    "fields": "status_code",
                    "access_token": token,
                }
            )
            status = s.json().get("status_code")
            if status == "FINISHED":
                break
            if status == "ERROR":
                raise Exception(f"Instagram container failed: {s.json()}")
            await asyncio.sleep(3)
        else:
            raise Exception("Instagram container timed out")

        # Step 3 — publish
        p = await client.post(
            f"{BASE}/{user_id}/media_publish",
            params={
                "creation_id": creation_id,
                "access_token": token,
            }
        )
        if p.is_error:
            raise Exception(f"Instagram publish error: {p.json()}")

    print(f"posted on the gram: {image_url}")
    return True
