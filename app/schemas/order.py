from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


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
