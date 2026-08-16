from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.address import Address
from app.schemas.address import AddressUpdateRequest
from app.services.user_service import UserService


class AddressService:
    def __init__(self, db: Session):
        self.db = db

    def update_address(self, req: AddressUpdateRequest, authorization: str) -> dict:
        """根据ID修改收货地址"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)
        address = self.db.query(Address).filter(Address.id == req.id).first()
        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="地址不存在"
            )
        if address.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权修改他人地址"
            )
        address.contact = req.contact
        address.phone = req.phone
        address.province = req.province
        address.city = req.city
        address.district = req.district
        address.address = req.address
        # 设为默认时，取消其他默认地址
        if req.is_default:
            self.db.query(Address).filter(
                Address.user_id == user_id,
                Address.is_default == True,
                Address.id != req.id
            ).update({"is_default": False})
        address.is_default = req.is_default
        self.db.commit()
        return {}
