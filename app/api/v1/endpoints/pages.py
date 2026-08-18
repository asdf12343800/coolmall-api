from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.page import GoodsDetailPageData, ConfirmOrderPageData
from app.schemas.user import ApiResponse
from app.services.page_service import PageService

router = APIRouter()


@router.get("/goodsDetail", response_model=ApiResponse[GoodsDetailPageData])
def get_goods_detail(
    goods_id: int = Query(..., alias="goodsId", description="商品ID"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """获取商品详情页面数据"""
    service = PageService(db)
    data = service.get_goods_detail(goods_id, authorization)
    return ApiResponse[GoodsDetailPageData](data=data)


@router.get("/confirmOrder", response_model=ApiResponse[ConfirmOrderPageData])
def get_confirm_order(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """获取确认订单页面数据"""
    service = PageService(db)
    data = service.get_confirm_order(authorization)
    return ApiResponse[ConfirmOrderPageData](data=data)
