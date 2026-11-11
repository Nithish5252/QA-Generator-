"""Read-only account inspection. Never creates accounts or resets passwords."""
import asyncio
import os
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.models import User

async def main():
    username = os.environ.get("CHECK_USERNAME")
    if not username:
        raise SystemExit("Set CHECK_USERNAME to inspect an account.")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if user:
            print(f"Account exists: active={user.is_active}, suspended={user.is_suspended}, role={user.role}")
        else:
            print("Account not found.")

if __name__ == "__main__":
    asyncio.run(main())
