from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.category import CategoryItem
from app.schemas.user import ApiResponse
from app.services.category_service import CategoryService

router = APIRouter()


@router.post("/list", response_model=ApiResponse[List[CategoryItem]])
def list_categories(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """查询所有启用的商品分类"""
    service = CategoryService(db)
    data = service.list_categories(authorization)
    return ApiResponse[List[CategoryItem]](data=data)
