"""Manual local login probe; credentials come only from the environment."""
import asyncio
import os
import httpx

async def main():
    username = os.environ.get("TEST_LOGIN_USERNAME")
    password = os.environ.get("TEST_LOGIN_PASSWORD")
    if not username or not password:
        raise SystemExit("Set TEST_LOGIN_USERNAME and TEST_LOGIN_PASSWORD.")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:8000/api/v1/auth/login",
            json={"username": username, "password": password},
        )
        # Never print response bodies: a successful response contains tokens.
        print(f"Status: {response.status_code}")

if __name__ == "__main__":
    asyncio.run(main())
