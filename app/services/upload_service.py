import json
import time
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.config import settings
from app.schemas.upload import UploadData, CosCredentials
from app.services.user_service import UserService


class UploadService:
    def __init__(self, db: Session):
        self.db = db

    def get_upload_credentials(self, authorization: str) -> UploadData:
        """获取腾讯云 COS 临时上传凭证"""
        user_service = UserService(self.db)
        user_id = user_service._get_user_id_from_token(authorization)

        if not settings.TENCENT_COS_SECRET_ID or not settings.TENCENT_COS_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="COS 配置缺失，请在 .env 中设置 TENCENT_COS_SECRET_ID / TENCENT_COS_SECRET_KEY",
            )

        duration = settings.TENCENT_COS_STS_DURATION
        request_id = str(uuid.uuid4())
        start_time = int(time.time())
        expired_time = start_time + duration
        expiration = (datetime.now(timezone.utc) + timedelta(seconds=duration)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        # 拼接 COS 桶 URL（格式: https://<bucket>-<appid>.cos.<region>.myqcloud.com）
        bucket = settings.TENCENT_COS_BUCKET
        appid = settings.TENCENT_COS_APPID
        region = settings.TENCENT_COS_REGION
        if bucket and appid and region:
            url = f"https://{bucket}-{appid}.cos.{region}.myqcloud.com"
        else:
            url = f"https://{bucket}.cos.{region}.myqcloud.com"

        try:
            tmp_secret_id, tmp_secret_key, session_token = self._issue_sts(duration)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取 STS 凭证失败: {e}",
            )

        return UploadData(
            credentials=CosCredentials(
                tmp_secret_id=tmp_secret_id,
                tmp_secret_key=tmp_secret_key,
                session_token=session_token,
            ),
            request_id=request_id,
            expiration=expiration,
            start_time=start_time,
            expired_time=expired_time,
            url=url,
        )

    def _issue_sts(self, duration: int) -> tuple[str, str, str]:
        """调用腾讯云 STS 申请临时凭证；失败时回退到占位实现便于本地调试"""
        try:
            from tencentcloud.common import credential
            from tencentcloud.sts.v20180813 import sts_client, models
        except ImportError:
            # tencentcloud-sdk-python 未安装时给出占位凭证，本地调试用
            return self._fallback_sts(duration)

        cred = credential.Credential(settings.TENCENT_COS_SECRET_ID, settings.TENCENT_COS_SECRET_KEY)
        client = sts_client.StsClient(cred, "")

        req = models.GetFederationTokenRequest()
        req.Name = f"coolmall-app-{uuid.uuid4().hex[:12]}"
        req.DurationSeconds = duration

        # 组装策略：限制到指定 COS 桶
        policy = settings.TENCENT_COS_STS_POLICY
        if not policy:
            bucket = settings.TENCENT_COS_BUCKET
            appid = settings.TENCENT_COS_APPID
            region = settings.TENCENT_COS_REGION
            resource = f"qcs::cos:{region}:uid/{appid}:{bucket}-{appid}/*"
            policy = json.dumps(
                {
                    "version": "2.0",
                    "statement": [
                        {
                            "effect": "allow",
                            "action": ["cos:PutObject", "cos:ListBucket", "cos:GetObject", "cos:HeadObject"],
                            "resource": [resource],
                        }
                    ],
                }
            )
        req.Policy = policy

        resp = client.GetFederationToken(req)
        return resp.Credentials.TmpSecretId, resp.Credentials.TmpSecretKey, resp.Credentials.Token

    def _fallback_sts(self, duration: int) -> tuple[str, str, str]:
        """STS SDK 未安装时的占位实现"""
        stub_id = f"STUB_TMP_SECRET_ID_{int(time.time())}"
        stub_key = f"STUB_TMP_SECRET_KEY_{uuid.uuid4().hex[:16]}"
        stub_token = f"STUB_SESSION_TOKEN_{uuid.uuid4().hex}"
        return stub_id, stub_key, stub_token
