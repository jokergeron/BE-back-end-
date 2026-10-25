# Sistem Manajemen Turnamen Esports REST API

[![Vercel Deployment](https://img.shields.io/badge/Vercel-Serverless%20WSGI-black?logo=vercel)](https://vercel.com)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.0-green?logo=flask)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%20(Supabase)-336791?logo=postgresql)](https://supabase.com)
[![Automated Tests](https://img.shields.io/badge/Automated%20Tests-22%20Passed-brightgreen)](test_api.py)
[![Postman Collection](https://img.shields.io/badge/Postman-v2.1%20Ready-FF6C37?logo=postman)](postman_collection.json)

Backend RESTful API untuk platform penyelenggaraan dan manajemen turnamen *esports*. Dibangun menggunakan **Python Flask** dan **PostgreSQL (Supabase)**, dengan dukungan deployment serverless WSGI pada platform **Vercel**. 

API ini mendukung operasi CRUD lengkap untuk data turnamen, filter status dan pencarian parsial, proteksi integritas relasional data pendaftaran tim, master data tim dan kapten, jadwal dan skor pertandingan, serta riwayat registrasi. Seluruh fungsi telah divalidasi dengan 22 skenario automated testing dan koleksi Postman yang memuat saved example response untuk seluruh status code (200, 201, 400, 404, 409).

---

## Fitur Utama

1. **CRUD Turnamen Lengkap (`/api/tournaments`)**:
   - `GET /api/tournaments`: Mengambil daftar turnamen dengan dukungan filter status (`?status=open|ongoing|completed`) dan pencarian nama (`?search=`).
   - `GET /api/tournaments/<id>`: Mengambil detail turnamen beserta relasi daftar tim yang terdaftar.
   - `POST /api/tournaments`: Membuat turnamen baru dilengkapi validasi wajib isi (`name`) dan kapasitas kuota positif (`max_teams`).
   - `PUT /api/tournaments/<id>`: Memperbarui data turnamen (`status`, `format`, `max_teams`).
   - `DELETE /api/tournaments/<id>`: Menghapus turnamen dengan **proteksi integritas relasional** (mengembalikan `409 Conflict` jika turnamen masih memiliki pendaftaran tim aktif).
2. **Master Data Tim, Pertandingan, & Registrasi**:
   - `GET /api/teams`: Mengambil data master tim esports beserta username kapten tim.
   - `GET /api/matches`: Mengambil jadwal pertandingan, skor tim A & B, serta nama pemenang.
   - `GET /api/registrations`: Mengambil riwayat pendaftaran tim ke turnamen beserta status verifikasi.
3. **Health Check, Routing Vercel & CORS**:
   - `GET /api/health`: Memeriksa uptime server backend dan konektivitas live ke PostgreSQL Supabase.
   - Dual-routing otomatis: Seluruh rute dapat diakses melalui `/api/<endpoint>` maupun langsung `/<endpoint>`.
   - Dukungan Cross-Origin Resource Sharing (CORS) global dan penanganan request preflight `OPTIONS` secara otomatis.
   - In-memory mock fallback: API tetap dapat berjalan mandiri jika database cloud sedang tidak terhubung.

---

## Diagram Relasi Basis Data (ERD)

Skema relasional 5 tabel utama yang didefinisikan pada `esports_db.sql`:

```mermaid
erDiagram
    USERS ||--o{ TEAMS : "captains"
    USERS ||--o{ TOURNAMENTS : "organizes"
    
    TOURNAMENTS ||--o{ REGISTRATIONS : "receives"
    TEAMS ||--o{ REGISTRATIONS : "registers"
    
    TOURNAMENTS ||--o{ MATCHES : "holds"
    TEAMS ||--o{ MATCHES : "plays_in"

    USERS {
        int id PK
        string username UK
        string email UK
        string password
        timestamp created_at
    }

    TEAMS {
        int id PK
        string name
        int captain_id FK
        timestamp created_at
    }

    TOURNAMENTS {
        int id PK
        int user_id FK
        string name
        string format
        int max_teams
        date start_date
        string status
    }

    REGISTRATIONS {
        int id PK
        int tournament_id FK
        int team_id FK
        timestamp registered_at
        string status
    }

    MATCHES {
        int id PK
        int tournament_id FK
        int team_a_id FK
        int team_b_id FK
        int winner_team_id FK
        int round
        int score_team_a
        int score_team_b
        timestamp match_date
    }
```

---

## Struktur Direktori Proyek

```text
BE-back-end-/
├── api/
│   ├── index.py              # Entrypoint Flask WSGI serverless Vercel & seluruh rute REST API
│   └── db.py                 # Driver koneksi PostgreSQL & fallback data mock
├── .env.example              # Template variabel lingkungan
├── .gitignore                # File yang diabaikan oleh Git
├── app.py                    # Runner lokal (python app.py)
├── esports_db.sql            # Skema DDL tabel database (idempoten: CREATE TABLE IF NOT EXISTS)
├── postman_collection.json   # Koleksi Postman v2.1 dengan skrip pm.test & saved examples (200, 201, 400, 404, 409)
├── README.md                 # Dokumentasi teknis proyek lengkap
├── requirements.txt          # Dependensi pustaka Python
├── seed.sql                  # Data awal dummy & sinkronisasi sequence auto-increment
├── SUBMISSION.md             # Format teks pengumpulan tugas
├── test_api.py               # Automated unit & integration tests (22 skenario)
└── vercel.json               # Konfigurasi routing serverless Vercel
```

---

## Panduan Setup Database (Supabase)

1. Buka dashboard [Supabase](https://supabase.com/) dan buat project baru.
2. Masuk ke menu **SQL Editor** pada navigasi kiri.
3. Buka file `esports_db.sql`, salin seluruh kodenya ke SQL Editor Supabase, lalu klik **Run**. Seluruh 5 tabel (`users`, `teams`, `tournaments`, `registrations`, `matches`) akan dibuat.
4. Buka file `seed.sql`, salin kodenya ke SQL Editor Supabase, lalu klik **Run**. Data dummy awal (T1, Fnatic, PRX, RRQ) akan dimasukkan dan nomor sequence SERIAL akan disinkronkan secara aman.
5. Ambil URI Connection String:
   - Buka **Project Settings** -> **Database**.
   - Pada bagian **Connection string**, pilih tab **URI**.
   - Contoh format:
     ```text
     postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres?sslmode=require
     ```
   - Catat URI ini untuk variabel lingkungan `.env` atau Vercel Environment Variables.

---

## Panduan Menjalankan Secara Lokal

### 1. Prasyarat
- Python 3.10 atau versi yang lebih baru
- Git

### 2. Langkah Instalasi & Menjalankan

1. **Clone Repositori**:
   ```bash
   git clone https://github.com/jokergeron/BE-back-end-.git
   cd BE-back-end-
   ```

2. **Buat Virtual Environment (Opsional tapi Direkomendasikan)**:
   ```bash
   python -m venv venv
   # Di Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # Di Linux/macOS:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Environment Variable (Opsional)**:
   Salin `.env.example` menjadi `.env` lalu masukkan connection string database:
   ```bash
   cp .env.example .env
   ```
   *Catatan: Jika `DATABASE_URL` tidak diisi, backend otomatis menggunakan in-memory mock data sehingga tetap dapat diuji tanpa konfigurasi database cloud.*

5. **Jalankan Aplikasi**:
   ```bash
   python app.py
   ```
   Aplikasi akan aktif di `http://127.0.0.1:5000`.

6. **Menjalankan Automated Tests**:
   ```bash
   python test_api.py
   ```

---

## Panduan Deployment ke Vercel

1. Pastikan seluruh perubahan kode telah di-commit dan di-push ke GitHub:
   ```bash
   git push origin main
   ```
2. Buka [Vercel Dashboard](https://vercel.com) dan login menggunakan akun GitHub Anda.
3. Klik **Add New...** -> **Project**.
4. Pilih dan impor repository `BE-back-end-`.
5. Pada bagian **Environment Variables**, tambahkan:
   - **Key**: `DATABASE_URL`
   - **Value**: Connection string URI dari Supabase Anda (`?sslmode=require`).
6. Klik **Deploy**. Vercel akan otomatis mengenali `api/index.py` melalui `vercel.json` dan mempublikasikan API secara serverless.

---

## Dokumentasi Lengkap REST API

### Ringkasan Daftar Endpoint

| HTTP Method | Endpoint URL | Status Code Sukses | Status Code Error | Deskripsi Singkat |
| :--- | :--- | :---: | :---: | :--- |
| `GET` | `/` | `200 OK` | - | Root index metadata layanan & katalog rute |
| `GET` | `/api/health` | `200 OK` | - | Status server backend & status database |
| `GET` | `/api/teams` | `200 OK` | - | Mengambil daftar tim esports beserta kaptennya |
| `GET` | `/api/matches` | `200 OK` | - | Mengambil jadwal, skor tim, dan pemenang pertandingan |
| `GET` | `/api/registrations` | `200 OK` | - | Mengambil riwayat pendaftaran tim pada turnamen |
| `GET` | `/api/tournaments` | `200 OK` | - | Mengambil daftar turnamen (filter status & pencarian) |
| `GET` | `/api/tournaments/<id>` | `200 OK` | `404 Not Found` | Detail data turnamen beserta tim yang terdaftar |
| `POST` | `/api/tournaments` | `201 Created` | `400 Bad Request` | Membuat entri turnamen baru (validasi input) |
| `PUT` | `/api/tournaments/<id>` | `200 OK` | `400 Bad Request`, `404 Not Found` | Memperbarui data turnamen yang ada |
| `DELETE` | `/api/tournaments/<id>` | `200 OK` | `404 Not Found`, `409 Conflict` | Menghapus turnamen (proteksi integritas relasional) |

---

### Detail Spesifikasi Setiap Endpoint

#### 1. Root API Index (`GET /`)
Mengambil informasi katalog metadata, nama layanan, versi API, dan tautan rute yang tersedia.

- **Method**: `GET`
- **URL**: `/` atau `/api/`
- **Headers**:
  - `Accept`: `application/json`
- **Request Body**: Tidak ada.
- **Success Response (`200 OK`)**:
  ```json
  {
    "endpoints": {
      "health": "/api/health",
      "matches": "/api/matches",
      "registrations": "/api/registrations",
      "teams": "/api/teams",
      "tournaments": "/api/tournaments"
    },
    "message": "Sistem Manajemen Turnamen Esports REST API siap digunakan",
    "service": "Esports Tournament Management REST API",
    "status": "success",
    "version": "1.0.0"
  }
  ```

---

#### 2. Health Check (`GET /api/health`)
Memeriksa status operasional runtime server backend dan status konektivitas live ke PostgreSQL Supabase.

- **Method**: `GET`
- **URL**: `/api/health`
- **Headers**:
  - `Accept`: `application/json`
- **Request Body**: Tidak ada.
- **Success Response (`200 OK`)**:
  ```json
  {
    "database": "connected",
    "service": "Esports Tournament API",
    "status": "healthy"
  }
  ```

---

#### 3. Master Data Teams (`GET /api/teams`)
Mengambil daftar seluruh tim esports yang terdaftar beserta informasi kapten tim.

- **Method**: `GET`
- **URL**: `/api/teams`
- **Headers**:
  - `Accept`: `application/json`
- **Request Body**: Tidak ada.
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "total": 4,
    "data": [
      {
        "id": 1,
        "name": "T1 Esports",
        "captain_id": 2,
        "captain_name": "faker_t1"
      },
      {
        "id": 2,
        "name": "Fnatic",
        "captain_id": 3,
        "captain_name": "boaster_fnc"
      },
      {
        "id": 3,
        "name": "Paper Rex",
        "captain_id": 4,
        "captain_name": "f0rsaken_prx"
      },
      {
        "id": 4,
        "name": "RRQ Hoshi",
        "captain_id": 5,
        "captain_name": "lemon_rrq"
      }
    ]
  }
  ```

---

#### 4. Master Data Matches (`GET /api/matches`)
Mengambil seluruh data pertandingan antar-tim esports, lengkap dengan ronde, nama tim, skor akhir, dan pemenang.

- **Method**: `GET`
- **URL**: `/api/matches`
- **Headers**:
  - `Accept`: `application/json`
- **Request Body**: Tidak ada.
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "total": 1,
    "data": [
      {
        "id": 1,
        "tournament_id": 1,
        "tournament_name": "Valorant Champions 2026",
        "round": 1,
        "team_a_name": "Fnatic",
        "team_b_name": "Paper Rex",
        "score_team_a": 1,
        "score_team_b": 2,
        "winner_name": "Paper Rex",
        "match_date": "2026-11-02 18:00:00"
      }
    ]
  }
  ```

---

#### 5. Master Data Registrations (`GET /api/registrations`)
Mengambil seluruh riwayat pendaftaran tim esports ke berbagai turnamen beserta status verifikasinya.

- **Method**: `GET`
- **URL**: `/api/registrations`
- **Headers**:
  - `Accept`: `application/json`
- **Request Body**: Tidak ada.
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "total": 3,
    "data": [
      {
        "id": 1,
        "tournament_id": 1,
        "team_id": 2,
        "team_name": "Fnatic",
        "status": "approved"
      },
      {
        "id": 2,
        "tournament_id": 1,
        "team_id": 3,
        "team_name": "Paper Rex",
        "status": "approved"
      },
      {
        "id": 3,
        "tournament_id": 2,
        "team_id": 4,
        "team_name": "RRQ Hoshi",
        "status": "approved"
      }
    ]
  }
  ```

---

#### 6. Get All Tournaments with Filtering (`GET /api/tournaments`)
Mengambil daftar turnamen dengan dukungan filtering status ketersediaan dan fitur pencarian nama.

- **Method**: `GET`
- **URL**: `/api/tournaments`
- **Query Parameters**:
  - `status` *(string, opsional)*: Menyaring status turnamen (`open`, `ongoing`, `completed`). Contoh: `?status=open`.
  - `search` *(string, opsional)*: Pencarian substring nama turnamen. Contoh: `?search=valorant`.
- **Headers**:
  - `Accept`: `application/json`
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "total": 3,
    "data": [
      {
        "id": 1,
        "name": "Valorant Champions 2026",
        "format": "Double Elimination",
        "max_teams": 16,
        "start_date": "2026-11-01",
        "status": "open",
        "organizer_id": 1,
        "organizer_name": "admin_esports"
      },
      {
        "id": 2,
        "name": "MPL Indonesia Season 18",
        "format": "Round Robin",
        "max_teams": 8,
        "start_date": "2026-11-15",
        "status": "open",
        "organizer_id": 1,
        "organizer_name": "admin_esports"
      },
      {
        "id": 3,
        "name": "League of Legends Worlds 2026",
        "format": "Swiss Stage",
        "max_teams": 16,
        "start_date": "2026-12-01",
        "status": "open",
        "organizer_id": 1,
        "organizer_name": "admin_esports"
      }
    ]
  }
  ```

---

#### 7. Get Tournament Detail By ID (`GET /api/tournaments/<id>`)
Mengambil informasi lengkap turnamen berdasarkan ID, termasuk relasi daftar tim yang terdaftar (`registered_teams`).

- **Method**: `GET`
- **URL**: `/api/tournaments/<id>` (Contoh: `/api/tournaments/1`)
- **Headers**:
  - `Accept`: `application/json`
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "data": {
      "id": 1,
      "name": "Valorant Champions 2026",
      "format": "Double Elimination",
      "max_teams": 16,
      "start_date": "2026-11-01",
      "status": "open",
      "organizer_id": 1,
      "organizer_name": "admin_esports",
      "registered_teams": [
        {
          "id": 1,
          "tournament_id": 1,
          "team_id": 2,
          "team_name": "Fnatic",
          "status": "approved"
        },
        {
          "id": 2,
          "tournament_id": 1,
          "team_id": 3,
          "team_name": "Paper Rex",
          "status": "approved"
        }
      ]
    }
  }
  ```
- **Error Response (`404 Not Found`)**:
  ```json
  {
    "status": "error",
    "message": "Turnamen dengan ID 9999 tidak ditemukan"
  }
  ```

---

#### 8. Create Tournament (`POST /api/tournaments`)
Membuat entri turnamen baru ke sistem. Dilengkapi validasi field wajib dan kuota tim.

- **Method**: `POST`
- **URL**: `/api/tournaments`
- **Headers**:
  - `Content-Type`: `application/json`
  - `Accept`: `application/json`
- **Request Body Parameters**:
  - `name` *(string, wajib)*: Nama lengkap turnamen esports.
  - `format` *(string, opsional)*: Format pertandingan (default: `Single Elimination`).
  - `max_teams` *(integer, opsional)*: Kuota maksimal tim, wajib berupa bilangan bulat positif (default: `16`).
  - `start_date` *(string, opsional)*: Tanggal mulai format `YYYY-MM-DD` (default: `2026-11-01`).
  - `user_id` *(integer, opsional)*: ID pengguna penyelenggara (default: `1`).
- **Contoh Request Body**:
  ```json
  {
    "name": "Dota 2 The International 2026",
    "format": "Double Elimination",
    "max_teams": 16,
    "start_date": "2026-10-15",
    "user_id": 1
  }
  ```
- **Success Response (`201 Created`)**:
  ```json
  {
    "status": "success",
    "message": "Turnamen berhasil dibuat",
    "data": {
      "id": 4,
      "name": "Dota 2 The International 2026",
      "format": "Double Elimination",
      "max_teams": 16,
      "start_date": "2026-10-15",
      "status": "open",
      "user_id": 1,
      "organizer_id": 1,
      "organizer_name": "admin_esports"
    }
  }
  ```
- **Error Response (`400 Bad Request` - Missing Name)**:
  ```json
  {
    "status": "error",
    "message": "Field 'name' turnamen wajib diisi"
  }
  ```
- **Error Response (`400 Bad Request` - Invalid Max Teams)**:
  ```json
  {
    "status": "error",
    "message": "Field 'max_teams' harus berupa integer positif"
  }
  ```

---

#### 9. Update Tournament (`PUT /api/tournaments/<id>`)
Memperbarui data turnamen yang sudah ada (status pelaksanaan, kapasitas kuota tim, format, atau nama turnamen).

- **Method**: `PUT`
- **URL**: `/api/tournaments/<id>` (Contoh: `/api/tournaments/1`)
- **Headers**:
  - `Content-Type`: `application/json`
  - `Accept`: `application/json`
- **Contoh Request Body**:
  ```json
  {
    "status": "ongoing",
    "max_teams": 24
  }
  ```
- **Success Response (`200 OK`)**:
  ```json
  {
    "status": "success",
    "message": "Data turnamen berhasil diperbarui",
    "data": {
      "id": 1,
      "name": "Valorant Champions 2026",
      "format": "Double Elimination",
      "max_teams": 24,
      "start_date": "2026-11-01",
      "status": "ongoing",
      "organizer_id": 1,
      "organizer_name": "admin_esports"
    }
  }
  ```
- **Error Response (`400 Bad Request` - Invalid Max Teams)**:
  ```json
  {
    "status": "error",
    "message": "Field 'max_teams' harus berupa integer positif"
  }
  ```
- **Error Response (`404 Not Found`)**:
  ```json
  {
    "status": "error",
    "message": "Turnamen dengan ID 9999 tidak ditemukan"
  }
  ```

---

#### 10. Delete Tournament with Relational Protection (`DELETE /api/tournaments/<id>`)
Menghapus data turnamen. API memiliki proteksi keamanan relasional: jika terdapat registrasi tim aktif pada turnamen tersebut, operasi penghapusan ditolak dengan status `409 Conflict`.

- **Method**: `DELETE`
- **URL**: `/api/tournaments/<id>` (Contoh: `/api/tournaments/1`)
- **Headers**:
  - `Accept`: `application/json`
- **Success Response (`200 OK` - Saat Tidak Ada Pendaftaran Terikat)**:
  ```json
  {
    "status": "success",
    "message": "Turnamen 'Dota 2 The International 2026' berhasil dihapus"
  }
  ```
- **Error Response (`409 Conflict` - Proteksi Integritas Relasional)**:
  ```json
  {
    "status": "error",
    "message": "Tidak dapat menghapus turnamen ID 1 karena masih terdapat 2 pendaftaran tim aktif (Relational Integrity Conflict)."
  }
  ```
- **Error Response (`404 Not Found`)**:
  ```json
  {
    "status": "error",
    "message": "Turnamen dengan ID 9999 tidak ditemukan"
  }
  ```

---

## Pengujian Postman

File koleksi `postman_collection.json` berstandar Postman Collection Schema v2.1 telah disertakan di root repositori:

1. Buka aplikasi **Postman** (atau ekstensi VS Code *Thunder Client* / *Postman*).
2. Klik tombol **Import**, lalu pilih file `postman_collection.json`.
3. Variabel `{{baseUrl}}` otomatis mengarah ke `http://127.0.0.1:5000` untuk pengetesan lokal.
   *(Saat menguji deployment Vercel, ubah nilai `baseUrl` menjadi URL Vercel Anda).*
4. Setiap request dalam koleksi telah dilengkapi dengan:
   - **Saved Example Responses** yang memuat respons nyata untuk status code `200`, `201`, `400`, `404`, dan `409`.
   - **Postman Test Scripts (`pm.test`)** untuk pengujian otomatis assertion status code, properti JSON, dan pesan validasi.
5. Jalankan seluruh pengujian sekaligus menggunakan fitur **Run collection** pada Postman. Seluruh pengujian akan lolos 100% (All Passed).

---

## Pengujian Otomatis (Automated Tests)

Test suite otomatis menggunakan pustaka standar Python `unittest` dan Flask test client (`test_api.py`), tanpa memerlukan instalasi library eksternal tambahan.

### Menjalankan Uji Otomatis:
```bash
python test_api.py
```

### Hasil Eksekusi Uji (22 Skenario - 100% Passed):
```text
Ran 22 tests in 0.070s

OK
```

### Cakupan 22 Skenario Pengujian:
1. `test_01_root_endpoint`: Validasi metadata root `/` status 200 dan daftar endpoint.
2. `test_02_health_check`: Validasi status `/api/health` 200 dan uptime database.
3. `test_03_get_teams`: Validasi pengambilan master data tim esports (total > 0).
4. `test_04_get_tournaments`: Validasi list seluruh turnamen esports.
5. `test_05_get_tournament_detail_success`: Validasi pengambilan detail turnamen ID 1 dan nested array `registered_teams`.
6. `test_06_get_tournament_detail_not_found`: Validasi status 404 ketika ID turnamen tidak ditemukan.
7. `test_07_create_tournament_success`: Validasi pembuatan turnamen baru status 201 Created.
8. `test_08_create_tournament_missing_name`: Validasi status 400 Bad Request jika nama turnamen kosong.
9. `test_09_create_tournament_invalid_max_teams`: Validasi status 400 Bad Request jika kuota tim non-positif (0 atau negatif).
10. `test_10_update_tournament_success`: Validasi pembaruan data turnamen status 200 OK.
11. `test_11_update_tournament_not_found`: Validasi status 404 pada update turnamen dengan ID non-existent.
12. `test_12_update_tournament_invalid_max_teams`: Validasi status 400 pada pembaruan kuota tim dengan nilai tidak valid.
13. `test_13_delete_tournament_conflict`: Validasi proteksi integritas relasional status 409 Conflict jika turnamen memiliki tim terdaftar.
14. `test_14_delete_tournament_not_found`: Validasi status 404 pada penghapusan turnamen dengan ID non-existent.
15. `test_15_delete_tournament_success`: Validasi siklus hidup: pembuatan turnamen baru tanpa registrasi dan penghapusan sukses status 200 OK.
16. `test_16_get_matches`: Validasi pengambilan data jadwal dan skor pertandingan.
17. `test_17_get_registrations`: Validasi pengambilan riwayat registrasi tim turnamen.
18. `test_18_get_tournaments_filter_status`: Validasi penyaringan query parameter `?status=open`.
19. `test_19_get_tournaments_search`: Validasi penyaringan query parameter pencarian `?search=valorant`.
20. `test_20_custom_404_handler`: Validasi penanganan rute tidak terdaftar dengan JSON 404 standard.
21. `test_21_cors_headers`: Validasi header `Access-Control-Allow-Origin: *` pada respons API.
22. `test_22_options_preflight`: Validasi respons HTTP `OPTIONS` preflight 204 No Content untuk browser modern.
