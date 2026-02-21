"""
Audit logging service for compliance and audit trails.
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.db import models
from datetime import datetime
import json


class AuditService:
    """Service for immutable audit logging."""
    
    @staticmethod
    def log_action(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        invoice_id: Optional[int] = None,
        raw_ocr_output: Optional[str] = None,
        ai_prompt: Optional[str] = None,
        ai_response: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> models.AuditLog:
        """Create an immutable audit log entry."""
        audit_log = models.AuditLog(
            user_id=user_id,
            invoice_id=invoice_id,
            action=action,
            raw_ocr_output=raw_ocr_output,
            ai_prompt=ai_prompt,
            ai_response=ai_response,
            metadata=json.dumps(metadata) if metadata else None,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def log_upload(
        db: Session,
        user_id: int,
        invoice_id: int,
        filename: str,
        file_size: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log invoice upload."""
        return AuditService.log_action(
            db=db,
            action="upload",
            user_id=user_id,
            invoice_id=invoice_id,
            metadata={"filename": filename, "file_size": file_size},
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_ocr_complete(
        db: Session,
        invoice_id: int,
        ocr_output: str
    ):
        """Log OCR completion."""
        return AuditService.log_action(
            db=db,
            action="ocr_complete",
            invoice_id=invoice_id,
            raw_ocr_output=ocr_output
        )
    
    @staticmethod
    def log_ai_suggestion(
        db: Session,
        invoice_id: int,
        ai_prompt: str,
        ai_response: str
    ):
        """Log AI suggestion generation."""
        return AuditService.log_action(
            db=db,
            action="ai_suggestion",
            invoice_id=invoice_id,
            ai_prompt=ai_prompt,
            ai_response=ai_response
        )
    
    @staticmethod
    def log_approval(
        db: Session,
        user_id: int,
        invoice_id: int,
        suggestion_id: int,
        approved: bool,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log suggestion approval or rejection."""
        action = "approve" if approved else "reject"
        return AuditService.log_action(
            db=db,
            action=action,
            user_id=user_id,
            invoice_id=invoice_id,
            metadata={"suggestion_id": suggestion_id, "approved": approved},
            ip_address=ip_address,
            user_agent=user_agent
        )


audit_service = AuditService()
