from pydantic import BaseModel
from typing import Optional, List

class DsjData(BaseModel):
    msj_no: str
    msj_cdate: str
    msj_uid: str
    msj_orig: str
    msj_remarks: Optional[str]
    msj_courier_id: Optional[str]
    courier_name: Optional[str]
    rdsj_no: str
    rmsj_date: str
    jumlah_bag: int
    jumlah_awb: Optional[float]
    jumlah_koli: Optional[float]
    jumlah_kg: Optional[float]