import json
from sqlalchemy.orm import Session
from app.models.complain import Complain
from app.schemas.complain import ComplainSubmitRequest
from app.services.user_service import UserService


class ComplainService:
    def __init__(self, db: Session):
        self.db = db

    def submit_complain(self, req: ComplainSubmitRequest, authorization: str) -> bool:
        """提交投诉举报"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        images_json = json.dumps(req.images, ensure_ascii=False) if req.images else None

        complain = Complain(
            user_id=user_id,
            target_type=req.target_type,
            target_id=req.target_id,
            images=images_json,
            contact=req.contact,
            type=req.type,
            content=req.content,
        )
        self.db.add(complain)
        self.db.commit()
        return True
