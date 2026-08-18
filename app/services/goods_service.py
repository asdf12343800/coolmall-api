import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.goods import GoodsSpec
from app.models.goods_info import Goods
from app.models.search_keyword import SearchKeyword
from app.models.comment import Comment
from app.schemas.goods import GoodsSpecListRequest, GoodsSpecItem, SearchKeywordItem, GoodsPageRequest, GoodsItem, GoodsPageData, CommentSubmitRequest, CommentPageRequest, CommentItem, CommentPageData
from app.schemas.address import Pagination
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

    def page_goods(self, req: GoodsPageRequest, authorization: str) -> GoodsPageData:
        """分页查询商品"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)  # 校验 token

        query = self.db.query(Goods).filter(Goods.status == 1)
        total = query.count()
        rows = (
            query.order_by(Goods.sort_num.asc(), Goods.id.desc())
            .offset((req.page - 1) * req.size)
            .limit(req.size)
            .all()
        )
        items = [
            GoodsItem(
                id=g.id,
                create_time=_fmt_std(g.created_at),
                update_time=_fmt_std(g.updated_at) if g.updated_at else _fmt_std(g.created_at),
                type_id=g.type_id,
                title=g.title,
                sub_title=g.sub_title,
                main_pic=g.main_pic,
                pics=_parse_images(g.pics),
                price=float(g.price),
                sold=g.sold,
                content=g.content,
                content_pics=_parse_images(g.content_pics),
                recommend=g.recommend,
                featured=g.featured,
                status=g.status,
                sort_num=g.sort_num,
                specs=None,
            )
            for g in rows
        ]
        return GoodsPageData(
            list=items,
            pagination=Pagination(total=total, size=req.size, page=req.page),
        )

    def get_goods(self, goods_id: int, authorization: str) -> GoodsItem:
        """根据ID查询单个商品"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)  # 校验 token

        g = self.db.query(Goods).filter(Goods.id == goods_id).first()
        if not g:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商品不存在"
            )
        return GoodsItem(
            id=g.id,
            create_time=_fmt_std(g.created_at),
            update_time=_fmt_std(g.updated_at) if g.updated_at else _fmt_std(g.created_at),
            type_id=g.type_id,
            title=g.title,
            sub_title=g.sub_title,
            main_pic=g.main_pic,
            pics=_parse_images(g.pics),
            price=float(g.price),
            sold=g.sold,
            content=g.content,
            content_pics=_parse_images(g.content_pics),
            recommend=g.recommend,
            featured=g.featured,
            status=g.status,
            sort_num=g.sort_num,
            specs=None,
        )

    def submit_comment(self, req: CommentSubmitRequest, authorization: str) -> bool:
        """提交商品评论"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        data = req.data
        comment = Comment(
            order_id=data.order_id,
            goods_id=int(data.goods_id),
            user_id=user_id,
            content=data.content,
            star_count=data.star_count,
            pics=json.dumps(data.pics, ensure_ascii=False) if data.pics else None,
        )
        self.db.add(comment)
        self.db.commit()
        return True

    def page_comments(self, req: CommentPageRequest, authorization: str) -> CommentPageData:
        """分页查询商品评论"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)  # 校验 token

        from app.models.user import User

        query = (
            self.db.query(Comment, User)
            .outerjoin(User, User.id == Comment.user_id)
            .filter(Comment.goods_id == int(req.goods_id))
        )
        total = query.count()
        rows = (
            query.order_by(Comment.id.desc())
            .offset((req.page - 1) * req.size)
            .limit(req.size)
            .all()
        )
        items = []
        for c, u in rows:
            try:
                order_id_val = int(c.order_id)
            except (TypeError, ValueError):
                order_id_val = 0
            items.append(
                CommentItem(
                    id=c.id,
                    create_time=_fmt_std(c.created_at),
                    update_time=_fmt_std(c.updated_at) if c.updated_at else _fmt_std(c.created_at),
                    user_id=c.user_id,
                    goods_id=c.goods_id,
                    order_id=order_id_val,
                    content=c.content,
                    star_count=c.star_count,
                    pics=_parse_images(c.pics) or [],
                    nick_name=(u.username if u and u.username else "") ,
                    avatar_url=(u.avatar if u else None),
                )
            )
        return CommentPageData(
            list=items,
            pagination=Pagination(total=total, size=req.size, page=req.page),
        )
