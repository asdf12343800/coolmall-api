from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field
from app.schemas.address import Pagination


class DiscountSource(BaseModel):
    type: Optional[int] = Field(default=None, description="折扣类型")
    object_id: Optional[int] = Field(default=None, alias="objectId", description="关联对象ID")
    info: Optional[Dict[str, Any]] = Field(default=None, description="折扣信息")


class UserAddressEntity(BaseModel):
    id: Optional[int] = None
    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_time: Optional[str] = Field(default=None, alias="updateTime")
    user_id: Optional[int] = Field(default=None, alias="userId")
    contact: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    is_default: Optional[bool] = Field(default=None, alias="isDefault")


class Logistics(BaseModel):
    company: Optional[str] = Field(default=None, description="物流公司")
    num: Optional[str] = Field(default=None, description="物流单号")


class Refund(BaseModel):
    order_num: Optional[str] = Field(default=None, alias="orderNum")
    amount: Optional[float] = None
    real_amount: Optional[float] = Field(default=None, alias="realAmount")
    status: Optional[int] = None
    apply_time: Optional[str] = Field(default=None, alias="applyTime")
    time: Optional[str] = None
    reason: Optional[str] = None
    refuse_reason: Optional[str] = Field(default=None, alias="refuseReason")


class GoodsSpecEntity(BaseModel):
    id: Optional[int] = None
    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_time: Optional[str] = Field(default=None, alias="updateTime")
    goods_id: Optional[int] = Field(default=None, alias="goodsId")
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    sort_num: Optional[int] = Field(default=None, alias="sortNum")
    images: Optional[List[str]] = None
    cover: Optional[str] = Field(default=None, description="规格封面图")


class GoodsInfoEntity(BaseModel):
    id: Optional[int] = None
    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_time: Optional[str] = Field(default=None, alias="updateTime")
    type_id: Optional[int] = Field(default=None, alias="typeId")
    title: Optional[str] = None
    sub_title: Optional[str] = Field(default=None, alias="subTitle")
    main_pic: Optional[str] = Field(default=None, alias="mainPic")
    pics: Optional[List[str]] = None
    price: Optional[float] = None
    sold: Optional[int] = None
    content: Optional[str] = None
    status: Optional[int] = None
    sort_num: Optional[int] = Field(default=None, alias="sortNum")
    specs: Optional[List[GoodsSpecEntity]] = None


class OrderGoodsEntity(BaseModel):
    id: Optional[int] = None
    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_time: Optional[str] = Field(default=None, alias="updateTime")
    order_id: Optional[int] = Field(default=None, alias="orderId")
    goods_id: Optional[int] = Field(default=None, alias="goodsId")
    price: Optional[float] = None
    discount_price: Optional[float] = Field(default=None, alias="discountPrice")
    count: Optional[int] = None
    remark: Optional[str] = None
    goods_info: Optional[GoodsInfoEntity] = Field(default=None, alias="goodsInfo")
    spec: Optional[GoodsSpecEntity] = None
    is_comment: Optional[int] = Field(default=None, alias="isComment")


class OrderUpdateRequest(BaseModel):
    id: Optional[int] = Field(default=None, description="订单ID")
    create_time: Optional[str] = Field(default=None, alias="createTime")
    update_time: Optional[str] = Field(default=None, alias="updateTime")
    user_id: Optional[int] = Field(default=None, alias="userId")
    title: Optional[str] = Field(default=None, description="订单标题")
    pay_type: Optional[int] = Field(default=None, alias="payType", description="支付类型")
    pay_time: Optional[str] = Field(default=None, alias="payTime", description="支付时间")
    order_num: Optional[str] = Field(default=None, alias="orderNum", description="订单号")
    status: Optional[int] = Field(default=None, description="订单状态")
    price: Optional[float] = Field(default=None, description="订单价格")
    discount_price: Optional[float] = Field(default=None, alias="discountPrice", description="折扣价")
    discount_source: Optional[DiscountSource] = Field(default=None, alias="discountSource")
    address: Optional[UserAddressEntity] = None
    logistics: Optional[Logistics] = None
    refund: Optional[Refund] = None
    refund_status: Optional[int] = Field(default=None, alias="refundStatus", description="退款状态")
    refund_apply_time: Optional[str] = Field(default=None, alias="refundApplyTime", description="退款申请时间")
    remark: Optional[str] = Field(default=None, description="备注")
    close_remark: Optional[str] = Field(default=None, alias="closeRemark", description="关闭备注")
    invoice: Optional[int] = Field(default=None, description="发票")
    wx_type: Optional[int] = Field(default=None, alias="wxType", description="微信类型")
    goods_list: Optional[List[OrderGoodsEntity]] = Field(default=None, alias="goodsList")


class RefundRequest(BaseModel):
    order_id: int = Field(..., alias="orderId", description="订单ID")
    reason: str = Field(..., description="退款原因")


class OrderCancelRequest(BaseModel):
    order_id: int = Field(..., alias="orderId", description="订单ID")
    remark: str = Field(..., description="取消原因")


class OrderPageRequest(BaseModel):
    page: int = Field(default=1, description="页码", ge=1)
    size: int = Field(default=10, description="每页条数", ge=1)
    sort: str = Field(default="desc", description="排序方向: asc/desc")
    order: str = Field(default="updateTime", description="排序字段")


class OrderItem(BaseModel):
    id: int
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")
    user_id: int = Field(..., alias="userId")
    title: Optional[str] = None
    pay_type: Optional[int] = Field(default=None, alias="payType")
    pay_time: Optional[str] = Field(default=None, alias="payTime")
    order_num: str = Field(..., alias="orderNum")
    status: int
    price: Optional[float] = None
    discount_price: Optional[float] = Field(default=None, alias="discountPrice")
    discount_source: Optional[DiscountSource] = Field(default=None, alias="discountSource")
    address: Optional[UserAddressEntity] = None
    logistics: Optional[Logistics] = None
    refund: Optional[Refund] = None
    refund_status: Optional[int] = Field(default=None, alias="refundStatus")
    refund_apply_time: Optional[str] = Field(default=None, alias="refundApplyTime")
    remark: Optional[str] = None
    close_remark: Optional[str] = Field(default=None, alias="closeRemark")
    invoice: Optional[int] = None
    wx_type: Optional[int] = Field(default=None, alias="wxType")
    goods_list: Optional[List[OrderGoodsEntity]] = Field(default=None, alias="goodsList")


class OrderPageData(BaseModel):
    list: List[OrderItem]
    pagination: Pagination


class OrderCreateGoodsItem(BaseModel):
    goods_info: GoodsInfoEntity = Field(..., alias="goodsInfo")
    spec: GoodsSpecEntity
    count: int = Field(..., description="购买数量")
    goods_id: int = Field(..., alias="goodsId", description="商品ID")


class OrderCreateData(BaseModel):
    remark: str = Field(..., description="订单备注")
    goods_list: List[OrderCreateGoodsItem] = Field(..., alias="goodsList")
    coupon_id: int = Field(..., alias="couponId", description="优惠券ID")
    address_id: int = Field(..., alias="addressId", description="收货地址ID")
    title: str = Field(..., description="订单标题")


class OrderCreateRequest(BaseModel):
    data: OrderCreateData


class OrderCreateResponse(BaseModel):
    id: int = Field(..., description="新建订单ID")


class OrderCountData(BaseModel):
    closed: int = Field(default=0, alias="已关闭", description="已关闭订单数")
    pending_shipment: int = Field(default=0, alias="待发货", description="待发货订单数")
    pending_payment: int = Field(default=0, alias="待付款", description="待付款订单数")
