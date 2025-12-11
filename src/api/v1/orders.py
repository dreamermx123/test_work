from fastapi import APIRouter, Depends, HTTPException, Query, Request
from httpx import HTTPStatusError

from api.v1.models.order import (OrderCreate, OrderCreatePayment,
                                 OrderCreateResponse)
from core.types import PageSize
from logger import logger
from services.order_service import OrderService, get_order_service

router = APIRouter()


@router.post(
    "/create-order",
    summary="Создание заказа",
    description="Создаёт заказ и возвращает ответ CRM.",
    response_model=OrderCreateResponse,
)
async def create_order(
    request: Request,
    order: OrderCreate,
    order_service: OrderService = Depends(get_order_service),
):

    try:
        result = await order_service.create_order(order)
        return result
    except HTTPStatusError as exc:
        try:
            detail = exc.response.json()
        except ValueError:
            detail = exc.response.text or "CRM вернул ошибку"

        logger.error(
            "RetailCRM %s: %s",
            exc.response.status_code,
            detail,
        )
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=detail,
        )


@router.get(
    "/",
    summary="Получить список заказов клиента",
)
async def get_customers(
    request: Request,
    customer_id: int = Query(..., gt=0, description="ID клиента в CRM"),
    page_number: int = Query(1, gt=0, le=1000),
    page_size: PageSize = Query(
        PageSize.small,
        description="Количество элементов на странице (20, 50 или 100)",
    ),
    order_service: OrderService = Depends(get_order_service),
):

    filters = {
        "page": page_number,
        "limit": int(page_size),
        "customerId": customer_id,
    }
    try:
        return await order_service.get_orders_by_user_id(filters)
    except HTTPStatusError as exc:
        try:
            detail = exc.response.json()
        except ValueError:
            detail = exc.response.text or "CRM вернул ошибку"

        logger.error(
            "RetailCRM %s: %s",
            exc.response.status_code,
            detail,
        )
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=detail,
        )


@router.post(
    "/create-order-payments",
    summary="Привязка платежа к заказу",
    description="Создаёт заказ в RetailCRM и возвращает ответ CRM.",
)
async def create_order_payments(
    request: Request,
    data: OrderCreatePayment,
    order_service: OrderService = Depends(get_order_service),
):

    try:
        result = await order_service.create_order_payments(data)
        return result
    except HTTPStatusError as exc:
        try:
            detail = exc.response.json()
        except ValueError:
            detail = exc.response.text or "CRM вернул ошибку"

        logger.error(
            "RetailCRM %s: %s",
            exc.response.status_code,
            detail,
        )
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=detail,
        )
