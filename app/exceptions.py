# belajar_fastapi/app/exceptions.py
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

async def general_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error at {request.url}: {repr(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": str(exc)}
    )

async def http_exception_handler_custom(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTPException", "status": exc.status_code, "message": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "Validation Error", "detail": exc.errors()}
    )