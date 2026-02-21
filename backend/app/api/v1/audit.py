"""
Audit log endpoints (admin only).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import models
from app.core.security import get_current_active_user, require_role
from pydantic import BaseModel

router = APIRouter()


class AuditLogResponse(BaseModel):
    """Audit log response schema."""
    id: int
    user_id: int
    invoice_id: int
    action: str
    raw_ocr_output: str
    ai_prompt: str
    ai_response: str
    metadata: str
    ip_address: str
    user_agent: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[AuditLogResponse])
async def list_audit_logs(
    skip: int = 0,
    limit: int = 100,
    invoice_id: int = None,
    user_id: int = None,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """List audit logs (admin only)."""
    query = db.query(models.AuditLog)
    
    if invoice_id:
        query = query.filter(models.AuditLog.invoice_id == invoice_id)
    
    if user_id:
        query = query.filter(models.AuditLog.user_id == user_id)
    
    audit_logs = query.order_by(models.AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    return audit_logs


@router.get("/{audit_log_id}", response_model=AuditLogResponse)
async def get_audit_log(
    audit_log_id: int,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    """Get specific audit log entry (admin only)."""
    audit_log = db.query(models.AuditLog).filter(
        models.AuditLog.id == audit_log_id
    ).first()
    
    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    return audit_log
