from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import os
import json
from functools import lru_cache
from datetime import timedelta
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ganti dengan secret key acak
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)  # Sesi akan kedaluwarsa setelah 30 menit
db = SQLAlchemy(app)

# Konfigurasi API Key Google Generative AI
os.environ["API_KEY"] = "AIzaSyDFhM4eagH5Rq-OK-BLmvzVz4p-Pczp15c"
genai.configure(api_key=os.environ["API_KEY"])

class User(db.Model):
    __tablename__ = 'users'  # Explicitly define table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

  
class Formulir(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='formulir')

    # Data diri yang akan disimpan di Formulir
    nama_lengkap = db.Column(db.String(100))
    tempat_lahir = db.Column(db.String(100))
    tanggal_lahir = db.Column(db.String(100))
    jenis_kelamin = db.Column(db.String(20))
    alamat = db.Column(db.String(200))
    asal_sekolah = db.Column(db.String(200))
    no_hp = db.Column(db.String(20))
    
    foto_path = db.Column(db.String(200))
    ijazah_path = db.Column(db.String(200))
    pembayaran_path = db.Column(db.String(200))

    verifikasi_status = db.Column(db.String(20), default='belum')




UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Login check decorator
def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Anda perlu masuk terlebih dahulu.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Fungsi untuk membuat sesi permanen
@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


# Username dan password admin (hardcoded)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Rute untuk login admin
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query user from database
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_admin and check_password_hash(user.password, password):
            session['admin_logged_in'] = True
            session['user_id'] = user.id
            flash('Login admin berhasil.')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau password admin salah.')
    
 

# Rute untuk logout admin
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)  # Hapus sesi admin
    flash('Anda telah berhasil logout sebagai admin.')
    return redirect(url_for('admin_login'))

# Login check decorator khusus untuk admin
def admin_login_required(f):
    def wrapper(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Anda perlu login sebagai admin terlebih dahulu.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Tetapkan nama endpoint secara eksplisit
@app.route('/admin_dashboard', endpoint="admin_dashboard_view")
@admin_login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')


# Rute untuk Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = 'remember_me' in request.form 

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if remember_me:
                session.permanent = True

            if not user.is_verified:
                return redirect(url_for('verifikasi'))
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah. Coba lagi.')
    
    return render_template('login.html')


# Folder untuk menyimpan file upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# verivikasi
@app.route('/verifikasi', methods=['GET', 'POST'])
@login_required
def verifikasi():
    user = User.query.get(session.get('user_id'))

    if not user:
        flash("User tidak ditemukan. Silakan login ulang.")
        return redirect(url_for('logout'))

    # Jika belum ada formulir untuk user, buat formulir baru
    formulir = Formulir.query.filter_by(user_id=user.id).first()

    if not formulir:
        formulir = Formulir(user_id=user.id)

    if request.method == 'POST':
        formulir.nama_lengkap = request.form['nama_lengkap']
        formulir.tempat_lahir = request.form['tempat_lahir']
        formulir.tanggal_lahir = request.form['tanggal_lahir']
        formulir.jenis_kelamin = request.form['jenis_kelamin']
        formulir.alamat = request.form['alamat']
        formulir.asal_sekolah = request.form['asal_sekolah']
        formulir.no_hp = request.form['no_hp']
        formulir.verifikasi_status = 'pending'

        # Upload file
        foto = request.files['foto']
        ijazah = request.files['ijazah']
        pembayaran = request.files['pembayaran']

        if foto:
            foto_filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
            formulir.foto_path = os.path.join('static/uploads', foto_filename)

        if ijazah:
            ijazah_filename = secure_filename(ijazah.filename)
            ijazah.save(os.path.join(app.config['UPLOAD_FOLDER'], ijazah_filename))
            formulir.ijazah_path = os.path.join('static/uploads', ijazah_filename)

        if pembayaran:
            pembayaran_filename = secure_filename(pembayaran.filename)
            pembayaran.save(os.path.join(app.config['UPLOAD_FOLDER'], pembayaran_filename))
            formulir.pembayaran_path = os.path.join('static/uploads', pembayaran_filename)

        db.session.add(formulir)
        db.session.commit()
        flash("Data berhasil dikirim. Mohon tunggu verifikasi admin.")
        return redirect(url_for('index'))

    return render_template('verifikasi.html', user=user)




# Rute untuk Registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            # Validasi format email
            validate_email(username)

            # Validasi panjang password
            if len(password) < 8:
                flash('Password harus minimal 8 karakter.')
                return render_template('register.html')

            if User.query.filter_by(username=username).first():
                flash('Username sudah ada. Silakan pilih yang lain.')
            else:
                hashed_password = generate_password_hash(password)  # Menggunakan hashing default
                new_user = User(username=username, password=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                flash('Registrasi berhasil! Silakan login.')
                return redirect(url_for('login'))
        
        except EmailNotValidError as e:
            flash(f"Email tidak valid: {e}. Pastikan format email benar.")
    
    return render_template('register.html')

@app.route('/admin/verifikasi')
@admin_login_required
def admin_verifikasi_list():
    pengguna = User.query.all() 
    return render_template('admin_verifikasi_list.html', pengguna=pengguna)

@app.route('/admin/verifikasi/<int:user_id>/<action>')
@admin_login_required
def proses_verifikasi(user_id, action):
    user = User.query.get_or_404(user_id)
    if action == 'terima':
        user.verifikasi_status = 'approved'
        user.is_verified = True
    elif action == 'tolak':
        user.verifikasi_status = 'rejected'
        user.is_verified = False
    db.session.commit()
    flash(f'Verifikasi untuk {user.username} berhasil di-{action}.')
    return redirect(url_for('admin_verifikasi_list'))


# Rute Utama Index
@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    user = User.query.get(session['user_id'])

    if user.verifikasi_status == 'pending':
        pesan = "Harap tunggu, permintaan Anda sedang diproses oleh admin."
    elif user.verifikasi_status == 'approved':
        pesan = "Verifikasi Anda telah disetujui. Selamat datang!"
    elif user.verifikasi_status == 'rejected':
        pesan = "Verifikasi Anda ditolak. Silakan kirim ulang data Anda."
    else:
        pesan = ""

    return render_template('index.html', pesan=pesan)


# Rute untuk Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Anda telah berhasil logout.')
    return redirect(url_for('login'))

# Rute untuk menghapus akun
@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(session['user_id'])
    if user:
        db.session.delete(user)
        db.session.commit()
        session.pop('user_id', None)
        flash('Akun Anda berhasil dihapus.')
    else:
        flash('Terjadi kesalahan saat menghapus akun.')
    return redirect(url_for('register'))

# Inisialisasi database otomatis
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Membuat tabel jika belum ada
    app.run(debug=True)
