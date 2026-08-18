import json
from sqlalchemy.orm import Session
from app.models.feedback import Feedback
from app.schemas.feedback import FeedbackSubmitRequest
from app.services.user_service import UserService


class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def submit_feedback(self, req: FeedbackSubmitRequest, authorization: str) -> bool:
        """提交意见反馈"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        feedback = Feedback(
            user_id=user_id,
            images=json.dumps(req.images, ensure_ascii=False),
            contact=req.contact,
            type=req.type,
            content=req.content,
        )
        self.db.add(feedback)
        self.db.commit()
        return True
