# 🚀 Sistem Pengumpulan Tugas Microservices (Jay-ASJ)

Proyek ini adalah implementasi sistem manajemen tugas mahasiswa berbasis Microservices yang dibangun untuk memenuhi tugas UTS Administrasi Server Jaringan. Sistem ini mengintegrasikan layanan Database, Object Storage, dan Web Server dalam lingkungan kontainer Docker.

# 📌 Fitur Utama

    - CRUD Operations: Input, tampilkan, ubah, dan hapus data tugas.

    - Dual Storage: Metadata disimpan di PostgreSQL, file fisik disimpan di MinIO Object Storage.

    - File Validation: Pembatasan ukuran unggahan file maksimal 5MB.

    - Database Management: Dilengkapi dengan Adminer untuk monitoring database via GUI.

    - Orchestration: Seluruh layanan dijalankan menggunakan Docker Compose.

# 🛠️ Arsitektur & Alokasi Port

Sistem ini berjalan pada host IP localhost dengan pembagian port sebagai berikut:

| Service | Port Host | Deskripsi Fungsi |
| ------| ------------------------- | --------------------------------- |
| Frontend | 8082 | Antarmuka Web (Nginx) |
| Backend API | 8080 | Logika sistem (FastAPI) |
| Adminer | 8081 | Database Management Tool |
| MinIO Console | 9001 | Dashboard Object Storage |

# 📂 Struktur Direktori

```
uts-asj-jay/
├── app/                # Backend API (Python FastAPI)
│   ├── main.py         # Otak aplikasi & logika CRUD
│   ├── Dockerfile      # Instruksi build image API
│   └── requirements.txt# Library Python (SQLAlchemy, MinIO, dll)
├── frontend/           # Interface (HTML, CSS, JS)
│   └── index.html      # Tampilan utama web
├── .env                # Variabel lingkungan (Kredensial)
└── docker-compose.yml  # File orkestrasi seluruh layanan
```

# 🚀 Cara Menjalankan Project
1. Clone Repositori:
```bash
git clone https://github.com/UsernameKamu/uts-asj-jay.git
cd uts-asj-jay
```
2. Konfigurasi Environment:
Pastikan file `.env` sudah terisi dengan kredensial PostgreSQL dan MinIO yang sesuai.

3. Build & Jalankan Docker Compose:
```bash
Build & Jalankan Docker Compose:
```

4. Akses Layanan:
- Web Frontend: `http://192.168.0.127:8082`
- API Docs: `http://192.168.0.127:8080/docs`
- Adminer: `http://192.168.0.127:8081`

# 🧠 Penjelasan Teknis Singkat
- API Backend (main.py): Menggunakan FastAPI untuk memproses data. Memiliki fitur Retry Logic untuk memastikan koneksi ke database stabil saat startup.

- Docker Compose: Mengintegrasikan semua layanan ke dalam satu jaringan virtual bernama jay-network sehingga antar kontainer bisa saling berkomunikasi dengan aman.

- Security: Kredensial dipisahkan menggunakan file .env untuk mencegah kebocoran data sensitif dalam kode program.
