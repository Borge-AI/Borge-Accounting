"""
Main FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import api_router
from app.db.database import engine
from app.db import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Accounting Assistant API",
    description="AI-powered accounting assistant platform for accounting firms",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_warnings():
    """Warn if running with default/empty secrets (set in Railway for production)."""
    if "change-me-in-production" in settings.SECRET_KEY:
        print("WARNING: Using default SECRET_KEY. Set SECRET_KEY in Railway Variables for production.")
    if not settings.OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not set. AI suggestions will fail until you set it in Railway Variables.")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "accounting-assistant-api"}
