import json
from sqlalchemy.orm import Session
from app.models.goods import GoodsSpec
from app.models.search_keyword import SearchKeyword
from app.schemas.goods import GoodsSpecListRequest, GoodsSpecItem, SearchKeywordItem
from app.services.user_service import UserService


def _fmt_std(dt):
    """格式化日期时间为标准字符串，None 返回空串"""
    if not dt:
        return ""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _parse_images(images_raw):
    """解析 images 字段为 list 或 None"""
    if not images_raw:
        return None
    try:
        data = json.loads(images_raw)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return None


class GoodsService:
    def __init__(self, db: Session):
        self.db = db

    def list_specs(self, req: GoodsSpecListRequest, authorization: str) -> list[GoodsSpecItem]:
        """查询商品的所有规格"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)  # 校验 token

        rows = (
            self.db.query(GoodsSpec)
            .filter(GoodsSpec.goods_id == req.goods_id)
            .order_by(GoodsSpec.sort_num.asc(), GoodsSpec.id.asc())
            .all()
        )
        return [
            GoodsSpecItem(
                id=s.id,
                create_time=_fmt_std(s.created_at),
                update_time=_fmt_std(s.updated_at) if s.updated_at else _fmt_std(s.created_at),
                goods_id=s.goods_id,
                name=s.name,
                price=float(s.price),
                stock=s.stock,
                sort_num=s.sort_num,
                images=_parse_images(s.images),
            )
            for s in rows
        ]

    def list_keywords(self, authorization: str) -> list[SearchKeywordItem]:
        """查询所有搜索关键词"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)  # 校验 token

        rows = (
            self.db.query(SearchKeyword)
            .order_by(SearchKeyword.sort_num.asc(), SearchKeyword.id.asc())
            .all()
        )
        return [
            SearchKeywordItem(
                id=k.id,
                create_time=_fmt_std(k.created_at),
                update_time=_fmt_std(k.updated_at) if k.updated_at else _fmt_std(k.created_at),
                name=k.name,
                sort_num=k.sort_num,
            )
            for k in rows
        ]
