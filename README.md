Proyek ini merupakan implementasi dari sistem manajemen tugas siswa XII TKJ 2 dengan teknologi Microservices yang dibuat untuk menyelesaikan tugas UTS  Administrasi Server Jaringan. Sistem yang diimplementasikan mengintegrasikan layanan Database, Object Storage, serta Web Server dengan layanan docker kontainer

📌 Fitur Utama
CRUD Operations: Input, tampilkan, ubah, dan hapus data tugas.

Dual Storage: Data metadata disimpan di PostgreSQL dan file fisik disimpan di MinIO Object Storage.

File Validation: Pengecekan batasan ukuran file unggahan maksimum 5MB.

Database Management: Terdapat Adminer sebagai tools untuk melakukan monitoring database melalui user interface.

Orchestration: Semua layanan berjalan dengan docker compose

Penjelasan Teknis Singkat
API Backend (main.py): Menggunakan FastAPI untuk memproses data. Memiliki fitur Retry Logic untuk memastikan koneksi ke database stabil saat startup.

Docker Compose: Mengintegrasikan semua layanan dalam satu jaringan virtual bernama jay-network, sehingga antara container dapat berkomunikasi secara aman.

Security: Kredensial dibuat terpisah menggunakan file .env untuk menghindari kebocoran data sensitif dalam kode program.
