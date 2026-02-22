"""
Invoice endpoints for document upload and processing.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import os
import uuid
from app.db.database import get_db
from app.db import models
from app.core.security import get_current_active_user
from app.core.config import settings
from app.services.audit_service import audit_service
from app.services.workflow_engine import run_workflow
from app.services.workflow_steps import DEFAULT_INVOICE_STEPS
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Create uploads directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class InvoiceResponse(BaseModel):
    """Invoice response schema."""
    id: int
    filename: str
    file_size: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceDetailResponse(InvoiceResponse):
    """Detailed invoice response with suggestions."""
    suggestions: List[dict]
    
    class Config:
        from_attributes = True


@router.post("/upload", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def upload_invoice(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Upload an invoice document for processing."""
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read file
    contents = await file.read()
    
    # Check file size
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_path = UPLOAD_DIR / f"{file_id}{file_ext}"
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create invoice record
    invoice = models.Invoice(
        filename=file.filename,
        file_path=str(file_path),
        file_size=len(contents),
        mime_type=file.content_type,
        uploaded_by=current_user.id,
        status=models.ProcessingStatus.UPLOADED
    )
    
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    
    # Log upload
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    audit_service.log_upload(
        db=db,
        user_id=current_user.id,
        invoice_id=invoice.id,
        filename=file.filename,
        file_size=len(contents),
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Process invoice via workflow (OCR → AI → rules → save; safe dataflow, audited)
    try:
        await process_invoice(db, invoice.id, current_user.id)
    except Exception as e:
        invoice.status = models.ProcessingStatus.ERROR
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}"
        )
    
    return invoice


async def process_invoice(db: Session, invoice_id: int, user_id: Optional[int] = None):
    """Process an invoice via the default workflow (OCR → AI → rules → save). Safe dataflow, every step audited."""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        return
    try:
        context = {
            "invoice_id": invoice_id,
            "file_path": invoice.file_path,
            "mime_type": invoice.mime_type,
            "user_id": user_id or invoice.uploaded_by,
        }
        run_workflow(
            trigger="invoice_uploaded",
            context=context,
            steps=DEFAULT_INVOICE_STEPS,
            db=db,
            user_id=user_id or invoice.uploaded_by,
            invoice_id=invoice_id,
        )
    except Exception:
        invoice.status = models.ProcessingStatus.ERROR
        db.commit()
        raise


@router.get("/", response_model=List[InvoiceResponse])
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List invoices for the current user."""
    invoices = db.query(models.Invoice).filter(
        models.Invoice.uploaded_by == current_user.id
    ).offset(skip).limit(limit).all()
    
    return invoices


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice(
    invoice_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get invoice details with suggestions."""
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Check access (user can only see their own invoices, unless admin)
    if invoice.uploaded_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this invoice"
        )
    
    suggestions = db.query(models.Suggestion).filter(
        models.Suggestion.invoice_id == invoice_id
    ).all()
    
    return {
        **invoice.__dict__,
        "suggestions": [
            {
                "id": s.id,
                "account_number": s.account_number,
                "vat_code": s.vat_code,
                "confidence_score": s.confidence_score,
                "risk_level": s.risk_level.value,
                "approval_status": s.approval_status.value,
                "notes": s.notes,
                "created_at": s.created_at
            }
            for s in suggestions
        ]
    }
