from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ganti ini sesuai dengan environment kamu
USER = "DEVFERDI"
PASSWORD = "F3rd1D3fidd"
HOST = "10.8.2.219"
PORT = "1521"
SERVICE_NAME = "ORIONRBN"  # Atau sesuai dengan Oracle kamu

# Format Thin mode
DATABASE_URL = f"oracle+oracledb://{USER}:{PASSWORD}@{HOST}:{PORT}/?service_name={SERVICE_NAME}"

# contoh tidak dengan connection pooling
# engine = create_engine(DATABASE_URL, echo=True)

# Engine dengan connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=10,             # Jumlah koneksi aktif dalam pool
    max_overflow=5,           # Tambahan koneksi sementara jika pool penuh
    pool_timeout=30,          # Tunggu max 30 detik untuk koneksi idle
    pool_recycle=1800,        # Recycle koneksi setiap 30 menit
    echo=False                # Ganti ke True jika butuh debug SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
