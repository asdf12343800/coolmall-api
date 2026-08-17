from fastapi import APIRouter
from app.api.v1.endpoints import users, addresses, payments, orders

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