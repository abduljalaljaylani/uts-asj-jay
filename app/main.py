version: '3.8'

services:
  # Database Service
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - jay-network

  # Object Storage Service
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_ROOT_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_ROOT_PASSWORD}
    volumes:
      - minio_data:/data
    ports:
      - "9001:9001"
    networks:
      - jay-network

  # Backend/API Service
  api:
    build: ./app
    ports:
      - "8080:8080"
    env_file: .env
    restart: always
    depends_on:
      - postgres
      - minio
    networks:
      - jay-network

  # Frontend Service
  frontend:
    image: nginx:alpine
    volumes:
      - ./frontend:/usr/share/nginx/html
    ports:
      - "8082:80"
    networks:
      - jay-network

  # Adminer
  adminer:
    image: adminer
    ports:
      - "8081:8080"
    networks:
      - jay-network

networks:
  jay-network:
    driver: bridge

volumes:
  postgres_data:
  minio_data:
root@debian:~/uts-asj-jay# ls
app  docker-compose.yml  frontend
root@debian:~/uts-asj-jay# cd app
root@debian:~/uts-asj-jay/app# ls
Dockerfile  main.py  requirements.txt
root@debian:~/uts-asj-jay/app# cat Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Jalankan API di port 8080 [cite: 32]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
root@debian:~/uts-asj-jay/app# cat main.py
import os
import io
import time
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from minio import Minio

# 1. KONFIGURASI ENV (Sesuai Soal) [cite: 43]
DB_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('POSTGRES_DB')}"
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
BUCKET_NAME = os.getenv("MINIO_BUCKET", "tugas-jay")

# 2. SETUP DATABASE (PostgreSQL) [cite: 14, 31, 38]
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TugasUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String)
    email = Column(String)
    foto_url = Column(String)

# Fungsi Retry agar tidak "Connection Refused" [cite: 53]
def init_db():
    retries = 10
    while retries > 0:
        try:
            Base.metadata.create_all(bind=engine)
            print("--- Database Jay Terhubung & Tabel Dibuat ---")
            return
        except OperationalError:
            retries -= 1
            print(f"--- DB Belum Siap, Menunggu... ({retries} sisa percobaan) ---")
            time.sleep(5)
    raise Exception("Gagal koneksi ke Database setelah beberapa kali percobaan.")

# 3. SETUP MINIO (Object Storage)
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ROOT_USER,
    secret_key=MINIO_ROOT_PASSWORD,
    secure=False
)

def init_minio():
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
        print(f"--- Bucket {BUCKET_NAME} Berhasil Dibuat ---")

# 4. INISIALISASI APP & CORS [cite: 32, 45]
app = FastAPI(title="API Pengumpulan Tugas Jay")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    init_minio()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINT CRUD [cite: 23, 29, 54] ---

# CREATE: Tambah Tugas & Foto [cite: 24, 25]
@app.post("/users")
async def create_user(
    nama: str = Form(...),
    email: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validasi file < 5MB
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File kegedean, Jay! Maksimal 5MB.")

    # Upload ke MinIO [cite: 25, 31]
    file_name = f"{int(time.time())}_{file.filename.replace(' ', '_')}"
    minio_client.put_object(
        BUCKET_NAME,
        file_name,
        io.BytesIO(content),
        len(content),
        content_type=file.content_type
    )

    # Simpan Metadata ke Postgres [cite: 25, 31]
    new_user = TugasUser(nama=nama, email=email, foto_url=file_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success", "message": "Data Jay Masuk!", "data": new_user}

# READ: Ambil Semua Data [cite: 26, 54]
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(TugasUser).all()

# DELETE: Hapus di DB & MinIO [cite: 28, 54]
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(TugasUser).filter(TugasUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Data tidak ada")

    # Hapus dari MinIO
    minio_client.remove_object(BUCKET_NAME, user.foto_url)

    # Hapus dari DB
    db.delete(user)
    db.commit()
    return {"message": f"Tugas id {user_id} berhasil dihapus dari sistem Jay"}
