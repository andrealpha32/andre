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

### Halaman Login
![Login](Screenshots/login.png)
*Halaman login untuk siswa dan admin*

### Dashboard Admin
![Dashboard Admin](Screenshots/dashboar%20admin.png)
*Panel kontrol untuk admin mengelola pendaftaran*

### Halaman Pendaftaran
![Form Pendaftaran](Screenshots/pendaftaran.png)
*Form pendaftaran siswa baru*

### Verifikasi Pendaftaran
![Verifikasi](Screenshots/ferivikasi.png)
*Halaman verifikasi data pendaftar*

### Dashboard Siswa
![Dashboard Siswa](static/Screenshots/dashboard siswa.png)
*Dashboard untuk siswa memantau status pendaftaran*

### Pembayaran
![Pembayaran](Screenshots/pembayaran.png)
*Halaman konfirmasi pembayaran*

### Kelola Jadwal
![Kelola Jadwal](Screenshots/kelola%20jadwal.png)
*Halaman admin untuk mengatur jadwal orientasi*

### Grup WhatsApp
![Grup WhatsApp](Screenshots/grup.png)
*Manajemen grup WhatsApp per jurusan*

### Forum Diskusi
![Forum](Screenshots/forum.png)
*Forum diskusi untuk siswa baru*

### Materi Persiapan
![Materi](Screenshots/materi.png)
*Halaman materi persiapan sekolah*

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

## Changelog

### [v1.0.0] - 2024-05-22
#### Added
- Sistem registrasi dan login untuk siswa dan admin
- Form pendaftaran online dengan upload dokumen
- Verifikasi pendaftaran oleh admin
- Sistem pembayaran dan upload bukti bayar
- Dashboard siswa dengan tracking progress
- Dashboard admin untuk manajemen data
- Forum diskusi untuk siswa baru
- Integrasi grup WhatsApp per jurusan
- Materi persiapan sekolah digital
- Jadwal orientasi siswa interaktif
- Kartu siswa digital dengan QR Code
- Sistem notifikasi status pendaftaran
- Checklist persiapan sekolah digital

#### Enhanced
- UI/UX dengan desain modern dan responsif
- Validasi form real-time
- Optimasi performa upload dokumen
- Sistem keamanan dan enkripsi data
- Dashboard dengan visualisasi data

#### Fixed
- Perbaikan bug pada upload file besar
- Optimasi query database
- Perbaikan tampilan di perangkat mobile
- Perbaikan validasi format dokumen
- Perbaikan sistem notifikasi

### [v0.9.0] - 2024-04-15
#### Added
- Prototype sistem pendaftaran dasar
- Form pendaftaran basic
- Login sistem
- Upload dokumen basic
- Dashboard sederhana

#### Fixed
- Bug pada sistem login
- Masalah kompatibilitas browser
- Error handling upload file

### [v0.8.0] - 2024-03-01
#### Added
- Konsep desain awal
- Struktur database dasar
- Template sistem basic