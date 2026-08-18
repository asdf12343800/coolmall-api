from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.param import SystemParam
from app.services.user_service import UserService


class ParamService:
    def __init__(self, db: Session):
        self.db = db

    def get_param(self, key: str, authorization: str) -> str:
        """根据 key 获取系统参数内容"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)

        row = self.db.query(SystemParam).filter(SystemParam.key == key).first()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"参数 {key} 不存在",
            )
        return row.content or ""
