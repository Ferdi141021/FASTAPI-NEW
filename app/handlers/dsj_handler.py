from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import text

from app.models import DsjData
from app.deps import get_db, get_api_key

router = APIRouter()

@router.get("/test")
def test_connection(db: Session = Depends(get_db)):
    return {"status": "connect to DB"}

@router.get("/dsj", response_model=List[DsjData])
def get_dsj(
    nomor_do: str = Query(..., min_length=5, max_length=30, regex=r"^[A-Z0-9\/\-]+$"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
):
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

    return [
        {
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
        }
        for row in rows
    ]