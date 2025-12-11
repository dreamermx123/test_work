import json
from functools import lru_cache

from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from api.v1.models.order import OrderCreate, OrderCreatePayment
from clients.crm_client import CrmClient, get_crm_client


class OrderService:
    def __init__(self, crm_client: CrmClient):
        self.crm_client = crm_client

    async def get_orders_by_user_id(self, filters: dict):
        params = {
            "limit": filters.get("limit"),
            "page": filters.get("page"),
            **{
                f"filter[{k}]": v
                for k, v in filters.items()
                if k not in ["page", "limit"]
            },
        }
        params = {k: v for k, v in params.items() if v is not None}

        return await self.crm_client.get(path="api/v5/orders", params=params)

    async def create_order(self, order_data: OrderCreate):
        payload = jsonable_encoder(order_data, exclude_none=True)

        return await self.crm_client.post(
            path="api/v5/orders/create",
            data={"order": json.dumps(payload, ensure_ascii=False)},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    async def create_order_payments(self, data: OrderCreatePayment):
        paid_at = data.payment.paidAt
        formatted_paid_at = paid_at.strftime("%Y-%m-%d %H:%M:%S")

        payment_dict = jsonable_encoder(data.payment, exclude_none=True)
        payment_dict["paidAt"] = formatted_paid_at

        return await self.crm_client.post(
            path="api/v5/orders/payments/create",
            data={"payment": json.dumps(payment_dict)},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )


@lru_cache()
def get_order_service(
    crm_client: CrmClient = Depends(get_crm_client),
) -> OrderService:
    return OrderService(crm_client)
