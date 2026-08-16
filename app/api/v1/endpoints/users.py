from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserResponse, UserUpdate, SmsCodeRequest, ApiResponse, RegisterRequest, RegisterTokenData, RefreshTokenRequest, PhoneLoginRequest, PasswordLoginRequest, CaptchaData, UpdatePersonRequest, UpdatePasswordRequest, BindPhoneRequest, PersonInfo, BindQQRequest

router = APIRouter()

@router.get("/login/captcha", response_model=ApiResponse[CaptchaData])
def get_captcha(
    type: str,
    width: int,
    height: int,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """获取图片验证码"""
    service = UserService(db)
    captcha_data = service.generate_captcha(type, width, height)
    return ApiResponse[CaptchaData](data=captcha_data)

@router.post("/login/smsCode", response_model=ApiResponse[str])
def send_sms_code(
    req: SmsCodeRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """发送短信验证码"""
    service = UserService(db)
    sms_code = service.send_sms_code(req)
    return ApiResponse[str](data=sms_code)

@router.post("/login/register", response_model=ApiResponse[RegisterTokenData])
def register(
    req: RegisterRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """用户注册"""
    service = UserService(db)
    token_data = service.register(req)
    return ApiResponse[RegisterTokenData](data=token_data)

@router.post("/login/refreshToken", response_model=ApiResponse[RegisterTokenData])
def refresh_token(
    req: RefreshTokenRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    service = UserService(db)
    token_data = service.refresh_token(req)
    return ApiResponse[RegisterTokenData](data=token_data)

@router.post("/login/phone", response_model=ApiResponse[RegisterTokenData])
def login_by_phone(
    req: PhoneLoginRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """手机号 + 短信验证码登录"""
    service = UserService(db)
    token_data = service.login_by_phone(req)
    return ApiResponse[RegisterTokenData](data=token_data)

@router.post("/login/password", response_model=ApiResponse[RegisterTokenData])
def login_by_password(
    req: PasswordLoginRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """手机号 + 密码登录"""
    service = UserService(db)
    token_data = service.login_by_password(req)
    return ApiResponse[RegisterTokenData](data=token_data)

@router.post("/info/updatePerson", response_model=ApiResponse[dict])
def update_person(
    req: UpdatePersonRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """更新当前登录用户的个人资料"""
    service = UserService(db)
    result = service.update_person(req, authorization)
    return ApiResponse[dict](data=result)

@router.post("/info/updatePassword", response_model=ApiResponse[dict])
def update_password(
    req: UpdatePasswordRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """更新当前登录用户的密码"""
    service = UserService(db)
    result = service.update_password(req, authorization)
    return ApiResponse[dict](data=result)

@router.post("/info/logoff", response_model=ApiResponse[dict])
def logoff(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """注销当前登录用户账号"""
    service = UserService(db)
    result = service.logoff(authorization)
    return ApiResponse[dict](data=result)

@router.post("/info/bindPhone", response_model=ApiResponse[dict])
def bind_phone(
    req: BindPhoneRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """绑定手机号"""
    service = UserService(db)
    result = service.bind_phone(req, authorization)
    return ApiResponse[dict](data=result)

@router.get("/info/person", response_model=ApiResponse[PersonInfo])
def get_person_info(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """获取当前登录用户的个人信息"""
    service = UserService(db)
    person_info = service.get_person_info(authorization)
    return ApiResponse[PersonInfo](data=person_info)

@router.post("/info/bindQQ", response_model=ApiResponse[dict])
def bind_qq(
    req: BindQQRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """绑定QQ账号"""
    service = UserService(db)
    result = service.bind_qq(req, authorization)
    return ApiResponse[dict](data=result)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    service = UserService(db)
    return service.create_user(user)

@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    service = UserService(db)
    return service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """获取单个用户"""
    service = UserService(db)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """更新用户"""
    service = UserService(db)
    user = service.update_user(user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    service = UserService(db)
    success = service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )