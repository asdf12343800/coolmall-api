from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.dict import DictDataRequest
from app.schemas.user import ApiResponse
from app.services.dict_service import DictService

router = APIRouter()


@router.post("/data", response_model=ApiResponse[dict])
def get_dict_data(
    req: DictDataRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """获得字典数据"""
    service = DictService(db)
    data = service.get_data(req, authorization)
    return ApiResponse[dict](data=data)
