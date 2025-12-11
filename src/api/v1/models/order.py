from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, PositiveFloat, conlist

from core.types import PaymentType


class OrderCustomer(BaseModel):
    id: int | None = None
    firstName: str = Field(..., description="Имя клиента")
    lastName: str = Field(..., description="Фамилия клиента")
    phone: str = Field(..., description="Телефон клиента")
    email: EmailStr | None = Field(
        default=None,
        description="Email клиента",
    )


class OrderOffer(BaseModel):
    externalId: str | None = Field(
        default=None,
        description="Внешний идентификатор SKU (если есть)",
    )
    id: int | None = Field(
        default=None,
        description="ID оффера в CRM",
    )


class OrderItem(BaseModel):
    offer: OrderOffer
    quantity: PositiveFloat = Field(..., description="Количество")
    initialPrice: PositiveFloat = Field(..., description="Цена за единицу")
    productName: str | None = Field(
        default=None,
        description="Название позиции",
    )


class DeliveryAddress(BaseModel):
    text: str = Field(..., description="Полный адрес")


class OrderDelivery(BaseModel):
    code: str = Field(..., description="Код способа доставки")
    cost: float = Field(
        default=0,
        description="Стоимость доставки",
    )
    address: DeliveryAddress | None = Field(
        default=None,
        description="Адрес доставки",
    )


class OrderCreate(BaseModel):
    site: str = Field(..., description="Символьный код магазина (site)")
    number: str = Field(..., description="Внешний номер заказа")
    status: str = Field(..., description="Код статуса заказа")
    orderMethod: str = Field(..., description="Способ оформления")
    customer: OrderCustomer
    items: conlist(OrderItem, min_length=1)
    delivery: OrderDelivery


class OrderCreateResponse(BaseModel):
    success: bool
    id: int | None = None
    order: dict | None = None


class PaymentOrder(BaseModel):
    id: str = Field(..., description="Внутренний ID заказа")
    number: str = Field(..., description="Номер заказа")


class Payment(BaseModel):
    externalId: str = Field(..., description="Внешний ID платежа")
    amount: PositiveFloat = Field(..., description="Количество")
    paidAt: datetime = Field(..., description="Дата оплаты")
    comment: str | None = None
    order: PaymentOrder
    type: PaymentType = Field(..., description="Тип оплаты")


class OrderCreatePayment(BaseModel):
    site: str = Field(..., description="Символьный код магазина (site)")
    payment: Payment
