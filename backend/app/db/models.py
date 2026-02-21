"""
Database models for the accounting assistant platform.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles."""
    ADMIN = "admin"
    ACCOUNTANT = "accountant"


class ProcessingStatus(str, enum.Enum):
    """Document processing status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    OCR_COMPLETE = "ocr_complete"
    AI_PROCESSING = "ai_processing"
    COMPLETE = "complete"
    ERROR = "error"


class ApprovalStatus(str, enum.Enum):
    """Suggestion approval status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RiskLevel(str, enum.Enum):
    """Risk level for suggestions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.ACCOUNTANT, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoices = relationship("Invoice", back_populates="uploaded_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Invoice(Base):
    """Invoice document model."""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String, nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(ProcessingStatus), default=ProcessingStatus.UPLOADED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    uploaded_by_user = relationship("User", back_populates="invoices")
    suggestions = relationship("Suggestion", back_populates="invoice", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="invoice")


class Suggestion(Base):
    """AI-generated accounting suggestion."""
    __tablename__ = "suggestions"
    
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    account_number = Column(String, nullable=True)
    vat_code = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=False)
    risk_level = Column(SQLEnum(RiskLevel), nullable=False)
    approval_status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    invoice = relationship("Invoice", back_populates="suggestions")
    approver = relationship("User", foreign_keys=[approved_by])


class AuditLog(Base):
    """Immutable audit log for compliance."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=True)
    action = Column(String, nullable=False)  # e.g., "upload", "ocr_complete", "ai_suggestion", "approve", "reject"
    raw_ocr_output = Column(Text, nullable=True)
    ai_prompt = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    invoice = relationship("Invoice", back_populates="audit_logs")
