"""
Suggestion endpoints for approval workflow.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.db import models
from app.core.security import get_current_active_user
from app.services.audit_service import audit_service
from pydantic import BaseModel

router = APIRouter()


class ApprovalRequest(BaseModel):
    """Approval request schema."""
    approved: bool
    notes: str = None


class SuggestionResponse(BaseModel):
    """Suggestion response schema."""
    id: int
    invoice_id: int
    account_number: str
    vat_code: str
    confidence_score: float
    risk_level: str
    approval_status: str
    notes: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.post("/{suggestion_id}/approve", response_model=SuggestionResponse)
async def approve_suggestion(
    suggestion_id: int,
    approval_request: ApprovalRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Approve or reject a suggestion."""
    suggestion = db.query(models.Suggestion).filter(
        models.Suggestion.id == suggestion_id
    ).first()
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    # Check access
    invoice = db.query(models.Invoice).filter(
        models.Invoice.id == suggestion.invoice_id
    ).first()
    
    if invoice.uploaded_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to approve this suggestion"
        )
    
    # Update suggestion
    if approval_request.approved:
        suggestion.approval_status = models.ApprovalStatus.APPROVED
        suggestion.approved_by = current_user.id
        suggestion.approved_at = datetime.utcnow()
    else:
        suggestion.approval_status = models.ApprovalStatus.REJECTED
        suggestion.approved_by = current_user.id
        suggestion.approved_at = datetime.utcnow()
    
    if approval_request.notes:
        suggestion.notes = approval_request.notes
    
    db.commit()
    db.refresh(suggestion)
    
    # Log approval/rejection
    ip_address = request.client.host if request else None
    user_agent = request.headers.get("user-agent") if request else None
    audit_service.log_approval(
        db=db,
        user_id=current_user.id,
        invoice_id=suggestion.invoice_id,
        suggestion_id=suggestion_id,
        approved=approval_request.approved,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return suggestion


@router.get("/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(
    suggestion_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get suggestion details."""
    suggestion = db.query(models.Suggestion).filter(
        models.Suggestion.id == suggestion_id
    ).first()
    
    if not suggestion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Suggestion not found"
        )
    
    # Check access
    invoice = db.query(models.Invoice).filter(
        models.Invoice.id == suggestion.invoice_id
    ).first()
    
    if invoice.uploaded_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this suggestion"
        )
    
    return suggestion
