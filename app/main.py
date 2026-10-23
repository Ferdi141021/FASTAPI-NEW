import logging
from fastapi import FastAPI
from app.handlers import dsj_handler, hdfs_handler, hive_handler
from app.exceptions import general_exception_handler, http_exception_handler_custom, validation_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

app = FastAPI()

app.include_router(dsj_handler.router)

app.include_router(hdfs_handler.router)

app.include_router(hive_handler.router)

app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(StarletteHTTPException,
                          http_exception_handler_custom)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
