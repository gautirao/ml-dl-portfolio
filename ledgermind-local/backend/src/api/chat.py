import logging
import time
import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from src.ai import (
    OllamaClient, Planner, validate_plan, 
    check_input_guardrail, AnswerGenerator, verify_answer,
    ChatResponse, Guardrails, AuditEvent
)
from src.ai.executor import execute_plan

logger = logging.getLogger(__name__)
router = APIRouter()

# In a real app, these would be injected via dependencies
ollama_client = OllamaClient()
planner = Planner(ollama_client)
answer_gen = AnswerGenerator(ollama_client)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

def log_audit_event(event_type: str, conversation_id: str, data: dict):
    event = AuditEvent(
        event_type=event_type,
        conversation_id=conversation_id,
        data=data
    )
    # For now, just log to standard logger. 
    # In a real app, this would go to a database or specialized audit log.
    logger.info(f"AUDIT_EVENT: {event.model_dump_json()}")

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    log_audit_event("chat_request_started", conversation_id, {"message_length": len(request.message)})
    
    # 1. Input Guardrail
    allowed, refusal = check_input_guardrail(request.message)
    if not allowed:
        log_audit_event("input_guardrail_refused", conversation_id, {"message": request.message})
        return ChatResponse(
            answer=refusal,
            guardrails=Guardrails(input_allowed=False, plan_valid=False, output_verified=True)
        )
    
    try:
        # 2. Planner
        plan = await planner.create_plan(request.message)
        log_audit_event("planner_completed", conversation_id, {"tool": plan.tool})
        
        # 3. Plan Validator
        is_valid, error_msg = validate_plan(plan)
        if not is_valid:
            log_audit_event("plan_validation_failed", conversation_id, {"error": error_msg})
            return ChatResponse(
                answer=f"I'm sorry, I couldn't process that request safely: {error_msg}",
                plan=plan,
                guardrails=Guardrails(input_allowed=True, plan_valid=False, output_verified=True)
            )
        
        # 4. Executor
        tool_result = await execute_plan(plan)
        log_audit_event("tool_execution_completed", conversation_id, {
            "tool": plan.tool, 
            "status": tool_result.execution_status,
            "latency_ms": int((time.time() - start_time) * 1000)
        })
        
        # 5. Answer Generator
        answer = await answer_gen.generate_answer(request.message, tool_result)
        log_audit_event("answer_generation_completed", conversation_id, {"tool": plan.tool})
        
        # 6. Result Verifier
        is_verified = verify_answer(answer, tool_result)
        if not is_verified:
            log_audit_event("answer_verification_failed", conversation_id, {"tool": plan.tool})
            # Fallback to deterministic answer
            answer = answer_gen.fallback_answer(tool_result)
        else:
            log_audit_event("answer_verification_completed", conversation_id, {"tool": plan.tool})
            
        return ChatResponse(
            answer=answer,
            plan=plan,
            tool_result=tool_result,
            evidence=tool_result.evidence,
            guardrails=Guardrails(
                input_allowed=True,
                plan_valid=True,
                output_verified=is_verified
            )
        )

    except Exception as e:
        logger.exception("Chat request failed")
        log_audit_event("chat_request_failed", conversation_id, {"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")
