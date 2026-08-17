import base64
import json
from datetime import datetime
from urllib.parse import quote_plus

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.order import Order
from app.schemas.payment import AlipayAppPayRequest
from app.services.user_service import UserService


# 订单状态
ORDER_STATUS_PENDING = 0  # 待付款
ORDER_STATUS_PAID = 1  # 已付款


def _load_private_key(key_str: str):
    """加载支付宝应用私钥，支持完整PEM或纯base64（PKCS8/PKCS1）"""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend

    key_str = key_str.strip()
    if "-----BEGIN" in key_str:
        return serialization.load_pem_private_key(
            key_str.encode("utf-8"),
            password=None,
            backend=default_backend(),
        )
    raw = key_str.replace(" ", "").replace("\n", "").replace("\r", "")
    for header, footer in (
        ("-----BEGIN PRIVATE KEY-----", "-----END PRIVATE KEY-----"),
        ("-----BEGIN RSA PRIVATE KEY-----", "-----END RSA PRIVATE KEY-----"),
    ):
        try:
            lines = [raw[i:i + 64] for i in range(0, len(raw), 64)]
            pem = header + "\n" + "\n".join(lines) + "\n" + footer
            return serialization.load_pem_private_key(
                pem.encode("utf-8"),
                password=None,
                backend=default_backend(),
            )
        except Exception:
            continue
    raise ValueError("无法解析私钥，请确认私钥格式为PKCS8或PKCS1")


class PaymentService:
    def __init__(self, db: Session):
        self.db = db

    def alipay_app_pay(self, req: AlipayAppPayRequest, authorization: str) -> str:
        """生成支付宝APP支付订单字符串"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        order = self.db.query(Order).filter(Order.id == req.order_id).first()
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="订单不存在",
            )
        if order.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权操作该订单",
            )
        if order.status != ORDER_STATUS_PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="订单状态不允许支付",
            )

        biz_content = {
            "out_trade_no": order.order_no,
            "total_amount": str(order.total_amount),
            "subject": settings.ALIPAY_SUBJECT,
        }
        params = {
            "app_id": settings.ALIPAY_APP_ID,
            "biz_content": json.dumps(biz_content, ensure_ascii=False),
            "charset": settings.ALIPAY_CHARSET,
            "format": "json",
            "method": "alipay.trade.app.pay",
            "notify_url": settings.ALIPAY_NOTIFY_URL,
            "sign_type": settings.ALIPAY_SIGN_TYPE,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
        }
        params["sign"] = self._sign(params)

        sorted_items = sorted(params.items(), key=lambda x: x[0])
        return "&".join(f"{k}={quote_plus(str(v))}" for k, v in sorted_items)

    def _sign(self, params: dict) -> str:
        """对请求参数做RSA2签名，返回base64编码的签名字符串"""
        if not settings.ALIPAY_APP_PRIVATE_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="支付宝应用私钥未配置",
            )
        sign_data = {k: v for k, v in params.items() if k not in ("sign", "sign_type")}
        sorted_items = sorted(sign_data.items(), key=lambda x: x[0])
        sign_str = "&".join(f"{k}={v}" for k, v in sorted_items)
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding

            private_key = _load_private_key(settings.ALIPAY_APP_PRIVATE_KEY)
            signature = private_key.sign(
                sign_str.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return base64.b64encode(signature).decode("utf-8")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"签名失败: {e}",
            )
