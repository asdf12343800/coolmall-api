from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.upload import UploadData
from app.schemas.user import ApiResponse
from app.services.upload_service import UploadService

router = APIRouter()


@router.post("/upload", response_model=ApiResponse[UploadData])
def get_upload_url(
    authorization: str = Header(...),
    db: Session = Depends(get_db),
):
    """获取文件上传地址（腾讯云 COS STS 临时凭证）"""
    service = UploadService(db)
    data = service.get_upload_credentials(authorization)
    return ApiResponse[UploadData](data=data)
