# PPDB Online System

Sistem Penerimaan Peserta Didik Baru (PPDB) Online adalah aplikasi web yang memudahkan proses pendaftaran siswa baru secara online. Aplikasi ini dibangun menggunakan Flask framework dengan tampilan modern dan responsif.

## Fitur Utama

### Untuk Calon Siswa
- Registrasi dan login akun
- Pengisian formulir pendaftaran online
- Upload dokumen persyaratan (Ijazah, Akta Kelahiran, dll)
- Tracking status pendaftaran
- Pembayaran biaya pendaftaran
- Akses materi persiapan sekolah
- Forum diskusi siswa
- Grup WhatsApp per jurusan
- Jadwal orientasi siswa

### Untuk Admin
- Dashboard admin
- Verifikasi pendaftaran siswa
- Manajemen jadwal orientasi
- Pengelolaan grup WhatsApp
- Pengelolaan materi persiapan
- Monitoring pembayaran

## Teknologi yang Digunakan

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: 
  - HTML5
  - Bootstrap 5
  - Bootstrap Icons
  - Chart.js
  - Custom CSS

## Screenshots

### Landing Page
![Landing Page](static/Screenshot/Screenshot_20.png)
*Halaman landing berisi informasi pendaftaran*

### Dashboard Siswa
![Dashboard](static/Screenshot/daftar.png)
(static/Screenshot/login.png)
(static/Screenshot/pendaftaran.png)
(static/Screenshot/.png)
*Dashboard siswa dengan status pendaftaran*

###siswa di verifikasi
![Form Pendaftaran](static/Screenshot/Screenshot.png)
*isi di dashboard siswa setelah di ferivikasi*

### Admin Dashboard
![Admin Dashboard](static/Screenshot/dashboar admin.png)
(static/Screenshot/ferivikasi.png)
(static/Screenshot/kelola jadwal.png)
(static/Screenshot/kelola grup.png)
*Dashboard admin untuk mengelola pendaftaran*

## Struktur Aplikasi

```
├── app.py                 # File utama aplikasi Flask
├── static/               # Aset statis
│   ├── styles.css       # CSS kustom
│   └── uploads/         # Folder upload dokumen
├── templates/           # Template HTML
│   ├── admin/          # Template halaman admin
│   ├── orientasi/      # Template halaman orientasi
│   └── *.html          # Template halaman utama
├── instance/           # Database SQLite
└── __pycache__/        # Python cache files
```

## Persyaratan Sistem

- Python 3.x
- Flask
- SQLite3
- Bootstrap 5
- Bootstrap Icons
- Chart.js

## Instalasi

1. Clone repositori ini:
```bash
git clone <repository-url>
```

2. Buat virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependensi:
```bash
pip install -r requirements.txt
```

4. Jalankan aplikasi:
```bash
python app.py
```

## Alur Pendaftaran

1. **Registrasi Akun**
   - Calon siswa membuat akun baru
   - Verifikasi email (opsional)

2. **Pengisian Formulir**
   - Input data pribadi
   - Upload dokumen persyaratan
   - Submit formulir

3. **Verifikasi Admin**
   - Admin memeriksa kelengkapan data
   - Verifikasi dokumen
   - Approval/reject pendaftaran

4. **Pembayaran**
   - Siswa melakukan pembayaran
   - Upload bukti pembayaran
   - Verifikasi pembayaran oleh admin

5. **Akses Fitur Siswa Baru**
   - Akses materi persiapan
   - Bergabung grup WhatsApp
   - Lihat jadwal orientasi
   - Partisipasi di forum siswa

## Kontribusi

Untuk berkontribusi pada proyek ini:

1. Fork repositori
2. Buat branch baru (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -am 'Menambahkan fitur baru'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request

## Lisensi

[MIT License](LICENSE)

## Kontak

Untuk informasi lebih lanjut, hubungi:
- Email: [email@domain.com]
- WhatsApp: [nomor-whatsapp]