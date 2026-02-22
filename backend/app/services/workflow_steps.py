"""
Default workflow steps for the invoice pipeline (safe dataflow).

Each step has declared allowed_inputs and allowed_outputs; the workflow engine
enforces that only these keys are read from / written to the context.
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.db import models
from app.services.ocr_service import ocr_service
from app.services.ai_service import ai_service
from app.services.rule_validation_service import rule_validation_service
from app.services.confidence_scoring_service import confidence_scoring_service
from app.services.audit_service import audit_service
from app.services.workflow_engine import StepDef


def _get_invoice(db: Session, invoice_id: int) -> models.Invoice:
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        raise ValueError(f"Invoice {invoice_id} not found")
    return invoice


def step_ocr(ctx: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Extract text from invoice file. Allowed in: invoice_id, file_path, mime_type. Out: ocr_text."""
    invoice_id = ctx["invoice_id"]
    file_path = ctx["file_path"]
    mime_type = ctx["mime_type"]
    invoice = _get_invoice(db, invoice_id)
    invoice.status = models.ProcessingStatus.PROCESSING
    db.commit()

    ocr_text = ocr_service.extract_text(file_path, mime_type)
    audit_service.log_ocr_complete(db=db, invoice_id=invoice_id, ocr_output=ocr_text)

    invoice.status = models.ProcessingStatus.OCR_COMPLETE
    db.commit()
    return {"ocr_text": ocr_text}


def step_ai_suggestion(ctx: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Call AI for accounting suggestion. In: ocr_text. Out: ai_result (dict). External – audited."""
    ocr_text = ctx["ocr_text"]
    invoice_id = ctx.get("invoice_id")
    invoice = _get_invoice(db, invoice_id) if invoice_id else None
    if invoice:
        invoice.status = models.ProcessingStatus.AI_PROCESSING
        db.commit()

    ai_prompt = ai_service.get_prompt_for_audit(ocr_text)
    ai_result = ai_service.generate_suggestion(ocr_text)
    if invoice_id:
        audit_service.log_ai_suggestion(
            db=db,
            invoice_id=invoice_id,
            ai_prompt=ai_prompt,
            ai_response=str(ai_result),
        )
    return {"ai_result": ai_result}


def step_rule_validation(ctx: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Apply rule validation and confidence scoring. In: ai_result. Out: risk_level, confidence_score, notes."""
    ai_result = ctx["ai_result"]
    final_confidence = confidence_scoring_service.calculate_final_confidence(
        ai_confidence=ai_result["confidence"],
        account_number=ai_result.get("account_number"),
        vat_code=ai_result.get("vat_code"),
    )
    risk_level = rule_validation_service.check_risk_rules(
        account_number=ai_result.get("account_number"),
        vat_code=ai_result.get("vat_code"),
        confidence=final_confidence,
    )
    notes = ai_result.get("reasoning", "")
    return {
        "risk_level": risk_level,
        "confidence_score": final_confidence,
        "notes": notes,
    }


def step_save_suggestion(ctx: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Persist suggestion and set invoice complete. In: invoice_id, ai_result, risk_level, confidence_score, notes. Out: (none)."""
    invoice_id = ctx["invoice_id"]
    ai_result = ctx["ai_result"]
    risk_level = ctx["risk_level"]
    confidence_score = ctx["confidence_score"]
    notes = ctx.get("notes", "")
    invoice = _get_invoice(db, invoice_id)

    suggestion = models.Suggestion(
        invoice_id=invoice_id,
        account_number=ai_result.get("account_number"),
        vat_code=ai_result.get("vat_code"),
        confidence_score=confidence_score,
        risk_level=risk_level,
        notes=notes,
    )
    db.add(suggestion)
    invoice.status = models.ProcessingStatus.COMPLETE
    db.commit()
    return {}


# Default workflow for trigger "invoice_uploaded": OCR → AI → Rules → Save
DEFAULT_INVOICE_STEPS: List[StepDef] = [
    StepDef(
        name="ocr",
        allowed_inputs=["invoice_id", "file_path", "mime_type"],
        allowed_outputs=["ocr_text"],
        is_external=False,
        run=step_ocr,
    ),
    StepDef(
        name="ai_suggestion",
        allowed_inputs=["ocr_text", "invoice_id"],
        allowed_outputs=["ai_result"],
        is_external=True,
        run=step_ai_suggestion,
    ),
    StepDef(
        name="rule_validation",
        allowed_inputs=["ai_result"],
        allowed_outputs=["risk_level", "confidence_score", "notes"],
        is_external=False,
        run=step_rule_validation,
    ),
    StepDef(
        name="save_suggestion",
        allowed_inputs=["invoice_id", "ai_result", "risk_level", "confidence_score", "notes"],
        allowed_outputs=[],
        is_external=False,
        run=step_save_suggestion,
    ),
]
