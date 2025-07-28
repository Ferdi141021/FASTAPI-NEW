# from datetime import datetime
import logging

# ✅ Konfigurasi logging lebih lengkap
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", mode='a', encoding='utf-8'),  # ✅ menulis ke file
        logging.StreamHandler()  # ✅ juga tampilkan ke console
    ]
)

from fastapi import FastAPI, Depends, Query, Security, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from database import SessionLocal
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

API_KEY = "mysecureapikey123"
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Pydantic response schema
class DsjData(BaseModel):
    msj_no: str
    msj_cdate: str
    msj_uid: str
    msj_orig: str
    msj_remarks: Optional[str]  # ✅ ubah jadi optional
    msj_courier_id: Optional[str]  # ✅ ubah jadi optional
    courier_name: Optional[str]
    rdsj_no: str
    rmsj_date: str
    jumlah_bag: int
    jumlah_awb: Optional[float]
    jumlah_koli: Optional[float]
    jumlah_kg: Optional[float]


# Dependency untuk ambil DB session
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

# ✅ Global exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error at {request.url}: {repr(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": str(exc)},
    )

# Untuk 404 / not found
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler_custom(request: Request, exc: StarletteHTTPException):
    logging.warning(f"HTTP error {exc.status_code} at {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "status": exc.status_code,
            "message": exc.detail,
        },
    )

# Untuk validation error (400)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors()
        },
    )

@app.get("/test")
def test_connection(db: Session = Depends(get_db)):
    return {"status": "connect to DB"}

@app.get("/dsj", response_model=List[DsjData])
def get_dsj(nomor_do: str = Query(..., min_length=5, max_length=30, regex=r"^[A-Z0-9\/\-]+$"), db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    sql = text("""
        SELECT  MSJ_NO,
                TO_CHAR(MSJ_CDATE, 'DD/MM/YYYY HH24:MI:SS') AS MSJ_CDATE,
                MSJ_UID,
                MSJ_ORIG,
                MSJ_REMARKS,
                MSJ_COURIER_ID,
                (SELECT COURIER_NAME FROM JNE.CMS_COURIER WHERE COURIER_ID = B.MSJ_COURIER_ID AND ROWNUM = 1) AS COURIER_NAME,
                RDSJ_NO,
                (SELECT TO_CHAR(RMSJ_DATE, 'DD/MM/YYYY HH24:MI:SS') FROM JNE.CMS_RMSJ WHERE RMSJ_NO = C.RDSJ_NO AND ROWNUM = 1) AS RMSJ_DATE,
                COUNT(RDSJ_BAG_NO) AS JUMLAH_BAG,
                SUM((SELECT BAG_CNOTE FROM JNE.CMS_MBAG_HO WHERE BAG_HO_NO = A.DSJ_HVO_NO AND BAG_NO = A.DSJ_BAG_NO)) AS JUMLAH_AWB,
                SUM((SELECT BAG_CNOTE_QTY FROM JNE.CMS_MBAG_HO WHERE BAG_HO_NO = A.DSJ_HVO_NO AND BAG_NO = A.DSJ_BAG_NO)) AS JUMLAH_KOLI,
                SUM((SELECT BAG_WEIGHT FROM JNE.CMS_MBAG_HO WHERE BAG_HO_NO = A.DSJ_HVO_NO AND BAG_NO = A.DSJ_BAG_NO)) AS JUMLAH_KG
        FROM JNE.CMS_DSJ A, JNE.CMS_MSJ B, JNE.CMS_RDSJ C
        WHERE DSJ_NO = MSJ_NO
        AND DSJ_BAG_NO = RDSJ_BAG_NO
        AND DSJ_HVO_NO = RDSJ_HVO_NO
        AND DSJ_NO = :nomor_do
        GROUP BY MSJ_NO, MSJ_CDATE, MSJ_UID, MSJ_ORIG, MSJ_REMARKS, MSJ_COURIER_ID, RDSJ_NO
    """)

    result = db.execute(sql, {"nomor_do": nomor_do})
    rows = result.fetchall()

    # Mapping manual ke dict
    data = []
    for row in rows:
        data.append({
            "msj_no": row[0],
            "msj_cdate": row[1],
            "msj_uid": row[2],
            "msj_orig": row[3],
            "msj_remarks": row[4],
            "msj_courier_id": row[5],
            "courier_name": row[6],
            "rdsj_no": row[7],
            "rmsj_date": row[8],
            "jumlah_bag": row[9],
            "jumlah_awb": row[10],
            "jumlah_koli": row[11],
            "jumlah_kg": row[12],
        })

    return data
