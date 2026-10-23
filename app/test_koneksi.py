from pyhive import hive


def test_hive():
    try:
        conn = hive.Connection(
            host="127.0.0.1",   # HiveServer2 yang dipublish ke host
            port=10000,
            username="hive",    # default user
            database="mydb",    # ganti kalau schema/db kamu beda
            auth="NOSASL"       # image hive kamu pakai NOSASL
        )
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        results = cursor.fetchall()
        print("✅ Koneksi berhasil!")
        print("Database tersedia:", results)
        conn.close()
    except Exception as e:
        print("❌ Gagal konek ke Hive:", e)


if __name__ == "__main__":
    test_hive()
