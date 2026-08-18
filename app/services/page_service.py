import json
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.goods_info import Goods
from app.models.coupon import Coupon, CouponUser
from app.models.comment import Comment
from app.models.user import User
from app.models.address import Address
from app.models.banner import Banner
from app.models.category import Category
from app.schemas.goods import GoodsItem, CommentItem
from app.schemas.coupon import CouponInfoItem, CouponCondition
from app.schemas.banner import BannerItem
from app.schemas.category import CategoryItem
from app.schemas.page import GoodsDetailPageData, ConfirmOrderPageData, UserCouponItem, DefaultAddress, HomePageData
from app.services.user_service import UserService


def _fmt_std(dt):
    if not dt:
        return ""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _parse_images(raw):
    if not raw:
        return None
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return None


def _build_goods_item(g: Goods) -> GoodsItem:
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


def _build_coupon_info_item(c: Coupon) -> CouponInfoItem:
    return CouponInfoItem(
        id=c.id,
        title=c.title,
        description="全场可用",
        type=c.type,
        amount=float(c.discount_value),
        num=c.stock,
        received_num=c.received,
        start_time=_fmt_std(c.start_time) or "",
        end_time=_fmt_std(c.end_time) or "",
        status=c.status,
        create_time=_fmt_std(c.created_at) or "",
        update_time=(_fmt_std(c.updated_at) if c.updated_at else (_fmt_std(c.created_at) or "")),
        condition=CouponCondition(full_amount=float(c.threshold)),
    )


class PageService:
    def __init__(self, db: Session):
        self.db = db

    def get_goods_detail(self, goods_id: int, authorization: str) -> GoodsDetailPageData:
        """获取商品详情页面数据"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)

        goods = self.db.query(Goods).filter(Goods.id == goods_id).first()
        if not goods:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="商品不存在",
            )

        goods_info = GoodsItem(
            id=goods.id,
            create_time=_fmt_std(goods.created_at),
            update_time=_fmt_std(goods.updated_at) if goods.updated_at else _fmt_std(goods.created_at),
            type_id=goods.type_id,
            title=goods.title,
            sub_title=goods.sub_title,
            main_pic=goods.main_pic,
            pics=_parse_images(goods.pics),
            price=float(goods.price),
            sold=goods.sold,
            content=goods.content,
            content_pics=_parse_images(goods.content_pics),
            recommend=goods.recommend,
            featured=goods.featured,
            status=goods.status,
            sort_num=goods.sort_num,
            specs=None,
        )

        coupons = (
            self.db.query(Coupon)
            .filter(Coupon.status == 1)
            .order_by(Coupon.id.asc())
            .all()
        )
        coupon_list = [
            CouponInfoItem(
                id=c.id,
                title=c.title,
                description="全场可用",
                type=c.type,
                amount=float(c.discount_value),
                num=c.stock,
                received_num=c.received,
                start_time=_fmt_std(c.start_time) or "",
                end_time=_fmt_std(c.end_time) or "",
                status=c.status,
                create_time=_fmt_std(c.created_at) or "",
                update_time=(_fmt_std(c.updated_at) if c.updated_at else (_fmt_std(c.created_at) or "")),
                condition=CouponCondition(full_amount=float(c.threshold)),
            )
            for c in coupons
        ]

        comments_query = (
            self.db.query(Comment, User)
            .outerjoin(User, User.id == Comment.user_id)
            .filter(Comment.goods_id == goods_id)
            .order_by(Comment.id.desc())
            .limit(5)
        )
        comment_rows = comments_query.all()
        comment_list = []
        for c, u in comment_rows:
            try:
                order_id_val = int(c.order_id)
            except (TypeError, ValueError):
                order_id_val = 0
            comment_list.append(
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
                    nick_name=(u.username if u and u.username else ""),
                    avatar_url=(u.avatar if u else None),
                )
            )

        return GoodsDetailPageData(
            goods_info=goods_info,
            coupon=coupon_list,
            comment=comment_list,
        )

    def get_confirm_order(self, authorization: str) -> ConfirmOrderPageData:
        """获取确认订单页面数据"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        user_coupon_rows = (
            self.db.query(CouponUser, Coupon)
            .outerjoin(Coupon, CouponUser.coupon_id == Coupon.id)
            .filter(CouponUser.user_id == user_id)
            .order_by(CouponUser.created_at.desc())
            .all()
        )
        user_coupon_list = []
        for cu, c in user_coupon_rows:
            if not c:
                continue
            user_coupon_list.append(
                UserCouponItem(
                    id=cu.id,
                    create_time=_fmt_std(cu.created_at),
                    update_time=(_fmt_std(cu.updated_at) if cu.updated_at else (_fmt_std(cu.created_at) or "")),
                    title=c.title,
                    description="全场可用",
                    type=c.type,
                    amount=float(c.discount_value),
                    num=c.stock,
                    received_num=c.received,
                    start_time=_fmt_std(c.start_time) or "",
                    end_time=_fmt_std(c.end_time) or "",
                    status=c.status,
                    condition=CouponCondition(full_amount=float(c.threshold)),
                    use_status=cu.status,
                )
            )

        available_coupons = (
            self.db.query(Coupon)
            .filter(Coupon.status == 1)
            .order_by(Coupon.id.asc())
            .all()
        )
        coupon_list = [
            CouponInfoItem(
                id=c.id,
                title=c.title,
                description="全场可用",
                type=c.type,
                amount=float(c.discount_value),
                num=c.stock,
                received_num=c.received,
                start_time=_fmt_std(c.start_time) or "",
                end_time=_fmt_std(c.end_time) or "",
                status=c.status,
                create_time=_fmt_std(c.created_at) or "",
                update_time=(_fmt_std(c.updated_at) if c.updated_at else (_fmt_std(c.created_at) or "")),
                condition=CouponCondition(full_amount=float(c.threshold)),
            )
            for c in available_coupons
        ]

        default_addr = (
            self.db.query(Address)
            .filter(Address.user_id == user_id, Address.is_default == True)
            .first()
        )
        default_address = None
        if default_addr:
            default_address = DefaultAddress(
                id=default_addr.id,
                create_time=_fmt_std(default_addr.created_at),
                update_time=_fmt_std(default_addr.updated_at) if default_addr.updated_at else _fmt_std(default_addr.created_at),
                user_id=default_addr.user_id,
                contact=default_addr.contact,
                phone=default_addr.phone,
                province=default_addr.province,
                city=default_addr.city,
                district=default_addr.district,
                address=default_addr.address,
                is_default=bool(default_addr.is_default),
            )

        return ConfirmOrderPageData(
            user_coupon=user_coupon_list,
            coupon=coupon_list,
            default_address=default_address,
        )

    def get_home(self, authorization: str) -> HomePageData:
        """获取首页数据"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)

        coupons = (
            self.db.query(Coupon)
            .filter(Coupon.status == 1)
            .order_by(Coupon.id.asc())
            .all()
        )
        coupon_list = [_build_coupon_info_item(c) for c in coupons]

        banners = (
            self.db.query(Banner)
            .filter(Banner.status == 1)
            .order_by(Banner.sort_num.asc(), Banner.id.asc())
            .all()
        )
        banner_list = [
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
            for b in banners
        ]

        goods_rows = (
            self.db.query(Goods)
            .filter(Goods.status == 1, Goods.featured == True)
            .order_by(Goods.sort_num.asc(), Goods.id.desc())
            .limit(10)
            .all()
        )
        goods_list = [_build_goods_item(g) for g in goods_rows]

        flash_sale_rows = (
            self.db.query(Goods)
            .filter(Goods.status == 1)
            .order_by(Goods.created_at.desc())
            .limit(4)
            .all()
        )
        flash_sale_list = [_build_goods_item(g) for g in flash_sale_rows]

        recommend_rows = (
            self.db.query(Goods)
            .filter(Goods.status == 1, Goods.recommend == True)
            .order_by(Goods.sort_num.asc(), Goods.id.desc())
            .limit(10)
            .all()
        )
        recommend_list = [_build_goods_item(g) for g in recommend_rows]

        all_categories = (
            self.db.query(Category)
            .filter(Category.status == 1)
            .order_by(Category.sort_num.asc(), Category.id.asc())
            .all()
        )
        category_all_list = [
            CategoryItem(
                id=cat.id,
                create_time=_fmt_std(cat.created_at),
                update_time=_fmt_std(cat.updated_at) if cat.updated_at else _fmt_std(cat.created_at),
                name=cat.name,
                parent_id=cat.parent_id,
                sort_num=cat.sort_num,
                pic=cat.pic,
                status=cat.status,
            )
            for cat in all_categories
        ]

        top_categories = (
            self.db.query(Category)
            .filter(Category.status == 1, Category.parent_id.is_(None))
            .order_by(Category.sort_num.asc(), Category.id.asc())
            .limit(10)
            .all()
        )
        category_list = [
            CategoryItem(
                id=cat.id,
                create_time=_fmt_std(cat.created_at),
                update_time=_fmt_std(cat.updated_at) if cat.updated_at else _fmt_std(cat.created_at),
                name=cat.name,
                parent_id=cat.parent_id,
                sort_num=cat.sort_num,
                pic=cat.pic,
                status=cat.status,
            )
            for cat in top_categories
        ]

        return HomePageData(
            coupon=coupon_list,
            banner=banner_list,
            goods=goods_list,
            flash_sale=flash_sale_list,
            recommend=recommend_list,
            category_all=category_all_list,
            category=category_list,
        )
