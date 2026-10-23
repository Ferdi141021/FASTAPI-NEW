from fastapi import APIRouter
import jaydebeapi
import jpype
import jpype.imports
from java.lang import Class  # akses ke java.lang.Class

router = APIRouter()

# Lokasi JAR Hive
JDBC_DRIVER_PATH = r"C:/Users/CWID/AppData/Roaming/DBeaverData/drivers/remote/timveil/hive-jdbc-uber-jar/releases/download/v1.9-2.6.5/hive-jdbc-uber-2.6.5.0-292.jar"


def get_hive_connection():
    jvm_path = jpype.getDefaultJVMPath()

    if not jpype.isJVMStarted():
        jpype.startJVM(jvm_path, f"-Djava.class.path={JDBC_DRIVER_PATH}")

    # Paksa load class driver Hive
    Class.forName("org.apache.hive.jdbc.HiveDriver")

    # Buat koneksi
    conn = jaydebeapi.connect(
        "org.apache.hive.jdbc.HiveDriver",
        "jdbc:hive2://172.18.0.11:10000/mydb;auth=noSasl",
        ["", ""],   # username / password kosong untuk NOSASL
    )
    return conn


@router.get("/hive_query/")
def hive_query(q: str):
    conn = get_hive_connection()
    cursor = conn.cursor()
    cursor.execute(q)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"rows": results}
