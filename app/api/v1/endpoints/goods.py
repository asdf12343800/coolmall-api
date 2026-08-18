from typing import List

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.goods import GoodsSpecListRequest, GoodsSpecItem, SearchKeywordItem
from app.schemas.user import ApiResponse
from app.services.goods_service import GoodsService

router = APIRouter()


@router.post("/spec/list", response_model=ApiResponse[List[GoodsSpecItem]])
def list_goods_specs(
    req: GoodsSpecListRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """查询商品的所有规格"""
    service = GoodsService(db)
    data = service.list_specs(req, authorization)
    return ApiResponse[List[GoodsSpecItem]](data=data)


@router.post("/search/keyword/list", response_model=ApiResponse[List[SearchKeywordItem]])
def list_search_keywords(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """查询所有搜索关键词"""
    service = GoodsService(db)
    data = service.list_keywords(authorization)
    return ApiResponse[List[SearchKeywordItem]](data=data)
