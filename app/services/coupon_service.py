from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.coupon import Coupon, CouponUser
from app.schemas.address import Pagination
from app.schemas.coupon import (
    CouponPageRequest, CouponPageData, CouponItem, CouponCondition, CouponUserItem,
)
from app.services.user_service import UserService


def _fmt_iso(dt):
    """格式化日期时间为 ISO 字符串"""
    if not dt:
        return ""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _fmt_std(dt):
    """格式化日期时间为标准字符串，None 返回 None"""
    if not dt:
        return None
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


class CouponService:
    def __init__(self, db: Session):
        self.db = db

    def receive(self, authorization: str) -> bool:
        """领取优惠券（占位实现：成功返回True）"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        # 占位：没有优惠券ID就返回成功，后续接口明确参数后补充逻辑
        return True

    def page_coupons(self, req: CouponPageRequest, authorization: str) -> CouponPageData:
        """分页查询当前用户已领取的优惠券"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        # 联表查询：用户领取记录 JOIN 优惠券主表
        query = (
            self.db.query(CouponUser, Coupon)
            .join(Coupon, CouponUser.coupon_id == Coupon.id)
            .filter(CouponUser.user_id == user_id)
        )

        order_map = {
            "updateTime": Coupon.updated_at,
            "createTime": Coupon.created_at,
            "id": Coupon.id,
        }
        sort_col = order_map.get(req.order, Coupon.updated_at)
        if req.sort == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        total = query.count()
        rows = query.offset((req.page - 1) * req.size).limit(req.size).all()

        items = [
            CouponItem(
                id=coupon.id,
                title=coupon.title,
                type=coupon.type,
                amount=float(coupon.discount_value),
                num=coupon.stock,
                received_num=coupon.received,
                description="全场可用",
                condition=CouponCondition(full_amount=float(coupon.threshold)),
                use_status=cu.status,
                status=coupon.status,
                start_time=_fmt_iso(coupon.start_time),
                end_time=_fmt_iso(coupon.end_time),
                create_time=_fmt_iso(coupon.created_at),
                update_time=_fmt_iso(coupon.updated_at) if coupon.updated_at else _fmt_iso(coupon.created_at),
            )
            for cu, coupon in rows
        ]
        return CouponPageData(
            list=items,
            pagination=Pagination(total=total, size=req.size, page=req.page),
        )

    def list_coupons(self, authorization: str) -> list[CouponUserItem]:
        """查询当前用户的所有优惠券领取记录"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        rows = (
            self.db.query(CouponUser)
            .filter(CouponUser.user_id == user_id)
            .order_by(CouponUser.created_at.desc())
            .all()
        )
        return [
            CouponUserItem(
                id=cu.id,
                create_time=_fmt_std(cu.created_at) or "",
                update_time=(_fmt_std(cu.updated_at) if cu.updated_at else (_fmt_std(cu.created_at) or "")),
                user_id=cu.user_id,
                coupon_id=cu.coupon_id,
                status=cu.status,
                use_time=_fmt_std(cu.used_time),
            )
            for cu in rows
        ]
