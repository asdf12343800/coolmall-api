from sqlalchemy.orm import Session
from app.models.dict import DictType, DictData
from app.schemas.dict import DictDataRequest, DictDataItem
from app.services.user_service import UserService


class DictService:
    def __init__(self, db: Session):
        self.db = db

    def get_data(self, req: DictDataRequest, authorization: str) -> dict:
        """根据类型名数组获取字典数据"""
        user_service = UserService(self.db)
        user_service._get_user_id_from_token(authorization)  # 校验 token

        # 查询所有请求的类型
        types = (
            self.db.query(DictType)
            .filter(DictType.type.in_(req.types))
            .all()
        )
        type_map = {t.type: t.id for t in types}
        type_ids = list(type_map.values())

        # 查询这些类型下的所有字典项
        rows = (
            self.db.query(DictData)
            .filter(DictData.type_id.in_(type_ids) if type_ids else False)
            .order_by(DictData.id.asc())
            .all()
        )

        # 按 type 字符串分组
        id_to_type = {v: k for k, v in type_map.items()}
        result = {t: [] for t in req.types}
        for d in rows:
            t_name = id_to_type.get(d.type_id)
            if not t_name:
                continue
            result.setdefault(t_name, []).append(
                DictDataItem(
                    type_id=d.type_id,
                    parent_id=d.parent_id,
                    name=d.name,
                    id=d.id,
                    value=d.value,
                )
            )
        return result
