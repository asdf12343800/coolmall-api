from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.feedback import FeedbackSubmitRequest
from app.schemas.user import ApiResponse
from app.services.feedback_service import FeedbackService

router = APIRouter()


@router.post("/submit", response_model=ApiResponse[bool])
def submit_feedback(
    req: FeedbackSubmitRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """提交意见反馈"""
    service = FeedbackService(db)
    data = service.submit_feedback(req, authorization)
    return ApiResponse[bool](data=data)
