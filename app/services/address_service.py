from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.address import Address
from app.schemas.address import AddressUpdateRequest, AddressPageRequest, AddressPageData, AddressItem, Pagination
from app.services.user_service import UserService


def _fmt(dt):
    """格式化日期时间为字符串"""
    if not dt:
        return ""
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


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

    def page_addresses(self, req: AddressPageRequest, authorization: str) -> AddressPageData:
        """分页查询当前用户的收货地址"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)
        query = self.db.query(Address).filter(Address.user_id == user_id)
        # 排序
        order_map = {
            "updateTime": Address.updated_at,
            "createTime": Address.created_at,
            "id": Address.id,
        }
        sort_col = order_map.get(req.order, Address.updated_at)
        if req.sort == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())
        # 分页
        total = query.count()
        items = query.offset((req.page - 1) * req.size).limit(req.size).all()
        return AddressPageData(
            list=[
                AddressItem(
                    id=a.id,
                    create_time=_fmt(a.created_at),
                    update_time=_fmt(a.updated_at) if a.updated_at else _fmt(a.created_at),
                    user_id=a.user_id,
                    contact=a.contact,
                    phone=a.phone,
                    province=a.province,
                    city=a.city,
                    district=a.district,
                    address=a.address,
                    is_default=a.is_default,
                )
                for a in items
            ],
            pagination=Pagination(total=total, size=req.size, page=req.page),
        )
