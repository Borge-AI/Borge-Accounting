"""
API v1 router.
"""
from fastapi import APIRouter
from app.api.v1 import auth, invoices, suggestions, audit

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(suggestions.router, prefix="/suggestions", tags=["suggestions"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
