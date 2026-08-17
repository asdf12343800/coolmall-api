from sqlalchemy.orm import Session
from app.models.banner import Banner
from app.schemas.banner import BannerItem
from app.services.user_service import UserService


def _fmt_std(dt):
    """格式化日期时间为标准字符串，None 返回空串"""
    if not dt:
        return ""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class BannerService:
    def __init__(self, db: Session):
        self.db = db

    def list_banners(self, authorization: str) -> list[BannerItem]:
        """查询所有启用的 banner"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)  # 校验 token

        rows = (
            self.db.query(Banner)
            .filter(Banner.status == 1)
            .order_by(Banner.sort_num.asc(), Banner.id.asc())
            .all()
        )
        return [
            BannerItem(
                id=b.id,
                create_time=_fmt_std(b.created_at),
                update_time=_fmt_std(b.updated_at) if b.updated_at else _fmt_std(b.created_at),
                description=b.description,
                path=b.path,
                pic=b.pic,
                sort_num=b.sort_num,
                status=b.status,
            )
            for b in rows
        ]
