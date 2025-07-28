from fastapi import Depends, Security, HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.security.api_key import APIKeyHeader
from .database import SessionLocal

API_KEY = "mysecureapikey123"
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API Key")
    return api_key