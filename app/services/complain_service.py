import json
from sqlalchemy.orm import Session
from app.models.complain import Complain
from app.schemas.complain import (
    ComplainSubmitRequest,
    ComplainPageRequest,
    ComplainPageData,
    ComplainItem,
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

    def page_complain(self, req: ComplainPageRequest, authorization: str) -> ComplainPageData:
        """分页查询当前用户的投诉举报"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        total = (
            self.db.query(Complain)
            .filter(Complain.user_id == user_id)
            .count()
        )

        offset = (req.page - 1) * req.size
        rows = (
            self.db.query(Complain)
            .filter(Complain.user_id == user_id)
            .order_by(Complain.id.desc())
            .offset(offset)
            .limit(req.size)
            .all()
        )

        items = [
            ComplainItem(
                id=c.id,
                create_time=_fmt_std(c.created_at),
                update_time=_fmt_std(c.updated_at) if c.updated_at else _fmt_std(c.created_at),
                user_id=c.user_id,
                target_type=c.target_type,
                target_id=c.target_id,
                contact=c.contact,
                type=c.type,
                content=c.content,
                images=parse_images(c.images),
                status=c.status or 0,
                handler_id=c.handler_id,
                remark=c.remark,
            )
            for c in rows
        ]
        return ComplainPageData(
            list=items,
            pagination=Pagination(total=total, size=req.size, page=req.page),
        )
