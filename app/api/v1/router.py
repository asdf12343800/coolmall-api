from fastapi import APIRouter
from app.api.v1.endpoints import users, addresses, payments, orders, coupons, coupon_infos, banners, categories, goods, dicts, chats, uploads

api_router = APIRouter()

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)

api_router.include_router(
    addresses.router,
    prefix="/user/address",
    tags=["addresses"]
)

api_router.include_router(
    payments.router,
    prefix="/app/order/pay",
    tags=["payments"]
)

api_router.include_router(
    orders.router,
    prefix="/app/order/info",
    tags=["orders"]
)

api_router.include_router(
    coupons.router,
    prefix="/app/market/coupon/user",
    tags=["coupons"]
)

api_router.include_router(
    coupon_infos.router,
    prefix="/app/market/coupon/info",
    tags=["coupon-infos"]
)

api_router.include_router(
    banners.router,
    prefix="/app/info/banner",
    tags=["banners"]
)

api_router.include_router(
    categories.router,
    prefix="/app/info/category",
    tags=["categories"]
)

api_router.include_router(
    goods.router,
    prefix="/app/goods",
    tags=["goods"]
)

api_router.include_router(
    dicts.router,
    prefix="/app/dict/info",
    tags=["dicts"]
)

api_router.include_router(
    chats.router,
    prefix="/app/cs",
    tags=["chats"]
)

api_router.include_router(
    uploads.router,
    prefix="/app/base/comm",
    tags=["uploads"]
)