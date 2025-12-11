# CRM API Gateway

Сервис на FastAPI, который проксирует запросы к RetailCRM: создаёт клиентов, заказы, платежи и отдаёт список заказов по клиенту.

## Требования

- Docker 24.x+
- Docker Compose 2.20+
- Git

_(Если нужно запускать без Docker — пригодится Python 3.11, но это опционально.)_

## Переменные окружения

Все настройки лежат в `src/.env`. Минимально нужно указать:

- PROJECT_NAME=CRM API
- BASE_URL=https://example.retailcrm.ru/
- API_KEY=your_api_key
- PORT=8000

## Запуск через Docker и docker-compose

git clone https://github.com/dreamermx123/test_work.git

cd test_work

# Собираем и поднимаем сервис

docker compose up --build

После старта:

- Healthcheck: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs

Логи приложения сохраняются на хосте в ./logs/app.log (каталог автоматически монтируется внутрь контейнера).

## Примеры запросов

### Создание заказа

```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders/create-order \
  -H "Content-Type: application/json" \
  -d '{
    "site": "your_site_code",
    "number": "TEST-ORDER-001",
    "status": "new",
    "orderMethod": "standard",
    "customer": {
      "firstName": "Иван",
      "lastName": "Иванов",
      "phone": "+79990000000",
      "email": "ivan@example.com"
    },
    "items": [
      {
        "offer": { "externalId": "SKU-001" },
        "quantity": 1,
        "initialPrice": 1990
      }
    ],
    "delivery": {
      "code": "self-delivery",
      "cost": 0,
      "address": { "text": "Москва, Тверская 1" }
    }
  }'
```

### Привязка платежа к заказу

```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders/create-order-payments \
  -H "Content-Type: application/json" \
  -d '{
    "site": "your_site_code",
    "payment": {
      "externalId": "PAY-123",
      "amount": 1990,
      "paidAt": "2025-12-11T03:01:33.014Z",
      "comment": "Оплата наличными в пункте выдачи",
      "order": {
        "id": "49А",
        "number": "TEST-ORDER-001"
      },
      "type": "cash"
    }
  }'
```
