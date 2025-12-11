from fastapi import FastAPI

from api.v1.customers import router as customer_router
from api.v1.orders import router as order_router
from core.config import settings
from core.logging import setup_logging
from middleware.request_logger import log_requests

setup_logging()

app = FastAPI(
    title=settings.project_name,
    docs_url="/docs",
    openapi_url="/api/openapi.json",
    root_path="/api",
)
app.middleware("http")(log_requests)
app.include_router(customer_router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(order_router, prefix="/api/v1/orders", tags=["orders"])


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=settings.port)
