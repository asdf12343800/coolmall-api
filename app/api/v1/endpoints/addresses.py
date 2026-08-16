from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.address_service import AddressService
from app.schemas.address import AddressUpdateRequest, AddressPageRequest, AddressPageData
from app.schemas.user import ApiResponse

router = APIRouter()


@router.post("/update", response_model=ApiResponse[dict])
def update_address(
    req: AddressUpdateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """根据ID修改收货地址"""
    service = AddressService(db)
    result = service.update_address(req, authorization)
    return ApiResponse[dict](data=result)


@router.post("/page", response_model=ApiResponse[AddressPageData])
def page_addresses(
    req: AddressPageRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """分页查询收货地址"""
    service = AddressService(db)
    data = service.page_addresses(req, authorization)
    return ApiResponse[AddressPageData](data=data)
