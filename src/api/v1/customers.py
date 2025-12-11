from datetime import date
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from httpx import HTTPStatusError
from pydantic import EmailStr

from api.v1.models.create_customer import (CustomerCreate,
                                           CustomerCreateResponse)
from api.v1.models.get_customer import CustomerResponse
from core.types import PageSize
from logger import logger
from services.customer_service import CustomerService, get_customer_service

router = APIRouter()


@router.post(
    "/create-customer",
    summary="Создание обычного клиента",
    description="Создает обычного клиента, возвращает статус запроса и id клиента",
    response_model=CustomerCreateResponse,
)
async def create_customer(
    request: Request,
    data: CustomerCreate,
    customer_service: CustomerService = Depends(get_customer_service),
) -> Any:

    try:
        return await customer_service.create_user(data)
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
    summary="Получить список обычных клиентов",
    response_model=list[CustomerResponse],
)
async def get_customers(
    request: Request,
    name: str | None = Query(
        default=None,
        min_length=2,
        max_length=50,
        description="Фильтр по имени клиента",
    ),
    email: EmailStr | None = Query(
        default=None,
        description="Фильтр по email клиента",
    ),
    registration_date_from: date | None = Query(
        default=None,
        description="Начало интервала регистрации (YYYY-MM-DD)",
    ),
    registration_date_to: date | None = Query(
        default=None,
        description="Конец интервала регистрации (YYYY-MM-DD)",
    ),
    page_number: int = Query(1, gt=0, le=1000),
    page_size: PageSize = Query(
        PageSize.small,
        description="Количество элементов на странице (20, 50 или 100)",
    ),
    customer_service: CustomerService = Depends(get_customer_service),
):

    if (
        registration_date_from
        and registration_date_to
        and registration_date_from > registration_date_to
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="registration_date_from не может быть позже registration_date_to",
        )

    filters: dict[str, any] = {
        "page_number": page_number,
        "page_size": page_size,
    }
    if name:
        filters["name"] = name.strip()
    if email:
        filters["email"] = email
    if registration_date_from:
        filters["dateFrom"] = registration_date_from
    if registration_date_to:
        filters["dateTo"] = registration_date_to

    try:

        return await customer_service.get_user(filters)

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
