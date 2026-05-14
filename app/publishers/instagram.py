import asyncio
import httpx

BASE = "https://graph.facebook.com/v21.0"


async def publish_to_instagram(image_url: str, user_id, token, caption: str = "") -> bool:
    if not user_id or not token:
        raise ValueError("No Instagram account connected. Connect your Instagram before publishing.")

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
            raise Exception(f"container creation failed [{r.status_code}]: {r.text}")
        creation_id = r.json().get("id")
        if not creation_id:
            raise Exception(f"no container id in response: {r.text}")

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
                raise Exception(f"container status ERROR: {s.text}")
            await asyncio.sleep(3)
        else:
            raise Exception(f"container timed out after 10 polls, last status: {status}")

        # Step 3 — publish
        p = await client.post(
            f"{BASE}/{user_id}/media_publish",
            params={
                "creation_id": creation_id,
                "access_token": token,
            }
        )
        if p.is_error:
            raise Exception(f"media_publish failed [{p.status_code}]: {p.text}")

    print(f"posted on the gram: {image_url}")
    return True
