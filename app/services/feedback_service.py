import json
from sqlalchemy.orm import Session
from app.models.feedback import Feedback
from app.schemas.feedback import (
    FeedbackSubmitRequest,
    FeedbackPageRequest,
    FeedbackPageData,
    FeedbackItem,
    parse_images,
)
from app.schemas.address import Pagination
from app.services.user_service import UserService


def _fmt_std(dt):
    if not dt:
        return ""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


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

    def page_feedback(self, req: FeedbackPageRequest, authorization: str) -> FeedbackPageData:
        """分页查询当前用户的反馈列表"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        total = (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .count()
        )

        offset = (req.page - 1) * req.size
        rows = (
            self.db.query(Feedback)
            .filter(Feedback.user_id == user_id)
            .order_by(Feedback.id.desc())
            .offset(offset)
            .limit(req.size)
            .all()
        )

        items = [
            FeedbackItem(
                id=f.id,
                create_time=_fmt_std(f.created_at),
                update_time=_fmt_std(f.updated_at) if f.updated_at else _fmt_std(f.created_at),
                user_id=f.user_id,
                contact=f.contact,
                type=f.type,
                content=f.content,
                images=parse_images(f.images),
                status=f.status or 0,
                handler_id=f.handler_id,
                remark=f.remark,
            )
            for f in rows
        ]
        return FeedbackPageData(
            list=items,
            pagination=Pagination(total=total, size=req.size, page=req.page),
        )
