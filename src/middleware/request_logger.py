from fastapi import Request

from logger import logger


async def log_requests(request: Request, call_next):
    body = await request.body()
    body_text = body.decode("utf-8", errors="replace") or "<empty>"

    logger.info(
        "HTTP %s %s params=%s body=%s",
        request.method,
        request.url.path,
        dict(request.query_params),
        body_text,
    )

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    request_with_body = Request(request.scope, receive)

    response = await call_next(request_with_body)
    return response
