from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.banner import BannerItem
from app.schemas.user import ApiResponse
from app.services.banner_service import BannerService

router = APIRouter()


@router.post("/list", response_model=ApiResponse[List[BannerItem]])
def list_banners(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """查询所有启用的 banner"""
    service = BannerService(db)
    data = service.list_banners(authorization)
    return ApiResponse[List[BannerItem]](data=data)
