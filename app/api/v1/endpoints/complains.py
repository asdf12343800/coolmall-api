from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.complain import ComplainSubmitRequest, ComplainPageRequest, ComplainPageData
from app.schemas.user import ApiResponse
from app.services.complain_service import ComplainService

router = APIRouter()


@router.post("/submit", response_model=ApiResponse[bool])
def submit_complain(
    req: ComplainSubmitRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """提交投诉举报"""
    service = ComplainService(db)
    data = service.submit_complain(req, authorization)
    return ApiResponse[bool](data=data)


@router.post("/page", response_model=ApiResponse[ComplainPageData])
def page_complain(
    req: ComplainPageRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """分页查询投诉举报"""
    service = ComplainService(db)
    data = service.page_complain(req, authorization)
    return ApiResponse[ComplainPageData](data=data)
