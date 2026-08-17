from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryItem
from app.services.user_service import UserService


def _fmt_std(dt):
    """格式化日期时间为标准字符串，None 返回空串"""
    if not dt:
        return ""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def list_categories(self, authorization: str) -> list[CategoryItem]:
        """查询所有启用的商品分类"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)  # 校验 token

        rows = (
            self.db.query(Category)
            .filter(Category.status == 1)
            .order_by(Category.sort_num.asc(), Category.id.asc())
            .all()
        )
        return [
            CategoryItem(
                id=c.id,
                create_time=_fmt_std(c.created_at),
                update_time=_fmt_std(c.updated_at) if c.updated_at else _fmt_std(c.created_at),
                name=c.name,
                parent_id=c.parent_id,
                sort_num=c.sort_num,
                pic=c.pic,
                status=c.status,
            )
            for c in rows
        ]
