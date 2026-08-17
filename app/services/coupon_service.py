from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.coupon import CouponUser
from app.services.user_service import UserService


class CouponService:
    def __init__(self, db: Session):
        self.db = db

    def receive(self, authorization: str) -> bool:
        """领取优惠券（占位实现：成功返回True）"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        # 占位：没有优惠券ID就返回成功，后续接口明确参数后补充逻辑
        return True
