from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_tenant_access
from app.models.user import User
from app.services.llm_service import llm_service
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/v1", tags=["assistant"])


class AskRequest(BaseModel):
    question: str


class SuggestedAction(BaseModel):
    action_type: str
    title: str
    description: str
    confidence: float


class AskResponse(BaseModel):
    answer: str
    suggested_actions: List[SuggestedAction]
    sources: List[str]
    confidence_score: float
    provenance: List[dict]


@router.post("/ask", response_model=AskResponse)
async def ask_assistant(
    request: AskRequest,
    x_tenant_id: str = Header(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ask the NLP assistant a question"""
    
    # Verify tenant access
    if not verify_tenant_access(current_user, x_tenant_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    try:
        # Process query using LLM service
        response = llm_service.process_ai_query(
            question=request.question,
            tenant_id=int(x_tenant_id),
            context={"user_id": current_user.id, "user_role": current_user.role}
        )
        
        # Convert suggested actions to response format
        suggested_actions = [
            SuggestedAction(
                action_type=action["action_type"],
                title=action["title"],
                description=action["description"],
                confidence=action["confidence"]
            )
            for action in response.get("suggested_actions", [])
        ]
        
        return AskResponse(
            answer=response["answer"],
            suggested_actions=suggested_actions,
            sources=response.get("sources", []),
            confidence_score=response.get("confidence_score", 0.5),
            provenance=response.get("provenance", [])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Assistant query failed: {str(e)}"
        )

