"""
Workflow engine: Zapier/Make-style steps with safe dataflow.

- Data moves only through a single context dict; each step has allowed inputs/outputs.
- Every step run and every external call is audited.
- Steps cannot read or write outside their allowed keys.
"""
from typing import Dict, Any, List, Callable, Optional
from sqlalchemy.orm import Session
import time

from app.db import models
from app.services import audit_service


# Type for a step runner: (context, db) -> context_updates
StepRunner = Callable[[Dict[str, Any], Session], Dict[str, Any]]


class StepDef:
    """Definition of a workflow step with safe dataflow."""
    def __init__(
        self,
        name: str,
        allowed_inputs: List[str],
        allowed_outputs: List[str],
        is_external: bool,
        run: StepRunner,
    ):
        self.name = name
        self.allowed_inputs = allowed_inputs
        self.allowed_outputs = allowed_outputs
        self.is_external = is_external  # True if step calls external API (audit request/response)
        self.run = run


def _filter_context(context: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
    """Return only allowed keys from context (safe input for a step)."""
    return {k: context[k] for k in allowed_keys if k in context}


def _validate_output(updates: Dict[str, Any], allowed_outputs: List[str]) -> None:
    """Raise if updates contain keys not in allowed_outputs."""
    for k in updates:
        if k not in allowed_outputs:
            raise ValueError(f"Step produced disallowed output key: {k}")


def run_workflow(
    trigger: str,
    context: Dict[str, Any],
    steps: List[StepDef],
    db: Session,
    user_id: Optional[int] = None,
    invoice_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run a workflow: execute steps in order, pass context, audit each step.

    - context: initial data (e.g. invoice_id, file_path, mime_type, user_id).
    - steps: list of StepDef. Each step receives only allowed_inputs from context,
      returns a dict of allowed_outputs which are merged into context for the next step.
    - user_id / invoice_id: used for audit logs.
    Returns final context.
    """
    for step in steps:
        start = time.time()
        input_keys = [k for k in step.allowed_inputs if k in context]
        try:
            step_input = _filter_context(context, step.allowed_inputs)
            updates = step.run(step_input, db)
            _validate_output(updates, step.allowed_outputs)
            context.update(updates)
            duration_ms = (time.time() - start) * 1000
            audit_service.log_action(
                db=db,
                action="workflow_step",
                user_id=user_id,
                invoice_id=invoice_id,
                metadata={
                    "trigger": trigger,
                    "step": step.name,
                    "input_keys": input_keys,
                    "output_keys": list(updates.keys()),
                    "success": True,
                    "duration_ms": round(duration_ms, 2),
                },
            )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            audit_service.log_action(
                db=db,
                action="workflow_step",
                user_id=user_id,
                invoice_id=invoice_id,
                metadata={
                    "trigger": trigger,
                    "step": step.name,
                    "input_keys": input_keys,
                    "output_keys": [],
                    "success": False,
                    "error": str(e),
                    "duration_ms": round(duration_ms, 2),
                },
            )
            raise
    return context
