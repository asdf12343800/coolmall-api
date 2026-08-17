from typing import List
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.address_service import AddressService
from app.schemas.address import AddressUpdateRequest, AddressPageRequest, AddressPageData, AddressItem, AddressDeleteRequest, AddressCreateRequest, AddressCreateResponse
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


@router.post("/list", response_model=ApiResponse[List[AddressItem]])
def list_addresses(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """查询当前用户的所有收货地址"""
    service = AddressService(db)
    data = service.list_addresses(authorization)
    return ApiResponse[List[AddressItem]](data=data)


@router.post("/delete", response_model=ApiResponse[dict])
def delete_addresses(
    req: AddressDeleteRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """批量删除收货地址"""
    service = AddressService(db)
    result = service.delete_addresses(req, authorization)
    return ApiResponse[dict](data=result)


@router.post("/add", response_model=ApiResponse[AddressCreateResponse])
def create_address(
    req: AddressCreateRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """新增收货地址"""
    service = AddressService(db)
    data = service.create_address(req, authorization)
    return ApiResponse[AddressCreateResponse](data=data)


@router.get("/info", response_model=ApiResponse[AddressItem])
def get_address(
    id: int,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """根据ID查询单个收货地址"""
    service = AddressService(db)
    data = service.get_address(id, authorization)
    return ApiResponse[AddressItem](data=data)
