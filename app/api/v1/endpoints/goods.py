from typing import List

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.goods import GoodsSpecListRequest, GoodsSpecItem, SearchKeywordItem, GoodsPageRequest, GoodsItem, GoodsPageData, CommentSubmitRequest, CommentPageRequest, CommentItem, CommentPageData
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


@router.post("/info/page", response_model=ApiResponse[GoodsPageData])
def page_goods(
    req: GoodsPageRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """分页查询商品"""
    service = GoodsService(db)
    data = service.page_goods(req, authorization)
    return ApiResponse[GoodsPageData](data=data)


@router.get("/info/info", response_model=ApiResponse[GoodsItem])
def get_goods(
    id: int = Query(..., description="商品ID"),
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """根据ID查询单个商品"""
    service = GoodsService(db)
    data = service.get_goods(id, authorization)
    return ApiResponse[GoodsItem](data=data)


@router.post("/comment/submit", response_model=ApiResponse[bool])
def submit_comment(
    req: CommentSubmitRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """提交商品评论"""
    service = GoodsService(db)
    data = service.submit_comment(req, authorization)
    return ApiResponse[bool](data=data)


@router.post("/comment/page", response_model=ApiResponse[CommentPageData])
def page_comments(
    req: CommentPageRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """分页查询商品评论"""
    service = GoodsService(db)
    data = service.page_comments(req, authorization)
    return ApiResponse[CommentPageData](data=data)
