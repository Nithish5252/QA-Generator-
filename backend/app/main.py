import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.core.config import settings
from app.core.database import init_db, AsyncSessionLocal
from app.core.middleware import SecurityAndLoggingMiddleware
from app.models.models import User
from app.core.security import get_password_hash
from app.api.v1.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("qa_platform_app")

async def seed_default_admin():
    # Bootstrap is opt-in. Never create shared or personal hardcoded accounts.
    if not settings.DEFAULT_ADMIN_PASSWORD:
        logger.info("Admin bootstrap disabled: no DEFAULT_ADMIN_PASSWORD configured.")
        return
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == settings.DEFAULT_ADMIN_USERNAME)
        )
        if result.scalars().first():
            return  # Never reset an existing account during startup.
        session.add(User(
            username=settings.DEFAULT_ADMIN_USERNAME,
            email=settings.DEFAULT_ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
            full_name="System Administrator",
            role="Admin",
            is_active=True,
            is_suspended=False,
        ))
        await session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Database Tables...")
    await init_db()
    logger.info("Database Tables Ready.")
    await seed_default_admin()
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Enterprise CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://frontend-two-alpha-53.vercel.app"
    ],
    allow_origin_regex="https://.*\\.vercel\\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Security & Logging Middleware
app.add_middleware(SecurityAndLoggingMiddleware)

# Include Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
