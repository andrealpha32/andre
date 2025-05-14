from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify, send_from_directory
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
    is_verified = db.Column(db.Boolean, default=False)  # Add this attribute
    formulir = db.relationship('Formulir', back_populates='user')  # Add this relationship

    def __repr__(self):
        return f'<User {self.username}>'

  
class Formulir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # Correct table name
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
    pembayaran_status = db.Column(db.String(20), default='belum') # Add this line

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
            # More detailed error message
            if not user:
                flash('Username tidak ditemukan.')
            elif not user.is_admin:
                flash('Akun ini bukan admin.')
            else:
                flash('Password salah.')
            
    return render_template('admin_login.html')  # Ensure a return statement for GET requests

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

    # Get existing formulir
    formulir = Formulir.query.filter_by(user_id=user.id).first()
    
    # If no formulir exists, create new one
    if not formulir and request.method == 'GET':
        formulir = Formulir(user_id=user.id)
        db.session.add(formulir)
        db.session.commit()

    if request.method == 'POST':
        if not formulir:
            formulir = Formulir(user_id=user.id)

        formulir.nama_lengkap = request.form['nama_lengkap']
        formulir.tempat_lahir = request.form['tempat_lahir']
        formulir.tanggal_lahir = request.form['tanggal_lahir']
        formulir.jenis_kelamin = request.form['jenis_kelamin']
        formulir.alamat = request.form['alamat']
        formulir.asal_sekolah = request.form['asal_sekolah']
        formulir.no_hp = request.form['no_hp']
        formulir.verifikasi_status = 'pending'

        # Handle file uploads with corrected paths
        foto = request.files.get('foto')
        ijazah = request.files.get('ijazah')
        pembayaran = request.files.get('pembayaran')

        if foto:
            foto_filename = secure_filename(foto.filename)
            foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
            formulir.foto_path = 'uploads/' + foto_filename  # Update path format

        if ijazah:
            ijazah_filename = secure_filename(ijazah.filename)
            ijazah.save(os.path.join(app.config['UPLOAD_FOLDER'], ijazah_filename))
            formulir.ijazah_path = 'uploads/' + ijazah_filename  # Update path format

        if pembayaran:
            pembayaran_filename = secure_filename(pembayaran.filename)
            pembayaran.save(os.path.join(app.config['UPLOAD_FOLDER'], pembayaran_filename))
            formulir.pembayaran_path = 'uploads/' + pembayaran_filename  # Update path format

        db.session.add(formulir)
        db.session.commit()
        flash("Data berhasil dikirim. Mohon tunggu verifikasi admin.")
        return redirect(url_for('index'))

    return render_template('verifikasi.html', user=user, formulir=formulir)

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
    # Query all users that have formulir data
    pengguna = User.query.join(Formulir).all()
    return render_template('admin_verifikasi_list.html', pengguna=pengguna)

@app.route('/admin/verifikasi/<int:user_id>/<action>')
@admin_login_required
def proses_verifikasi(user_id, action):
    user = User.query.get_or_404(user_id)
    formulir = Formulir.query.filter_by(user_id=user.id).first()

    if not formulir:
        flash("Formulir belum diisi oleh pengguna ini.")
        return redirect(url_for('admin_verifikasi_list'))

    if action == 'terima':
        formulir.verifikasi_status = 'approved'
        user.is_verified = True
    elif action == 'tolak':
        formulir.verifikasi_status = 'rejected'
        user.is_verified = False

    db.session.commit()
    flash(f'Verifikasi untuk {user.username} berhasil di-{action}.')
    return redirect(url_for('admin_verifikasi_list'))



# Rute Utama Index
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return render_template('landing.html')
        
    user = User.query.get(session['user_id'])
    formulir = Formulir.query.filter_by(user_id=user.id).first()

    if formulir:
        if formulir.verifikasi_status == 'pending':
            pesan = "Harap tunggu, permintaan Anda sedang diproses oleh admin."
        elif formulir.verifikasi_status == 'approved':
            pesan = "Verifikasi Anda telah disetujui. Selamat datang!"
        elif formulir.verifikasi_status == 'rejected':
            pesan = "Verifikasi Anda ditolak. Silakan kirim ulang data Anda."
        else:
            pesan = ""
    else:
        pesan = ""

    return render_template('index.html', user=user, formulir=formulir, pesan=pesan)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    formulir = Formulir.query.filter_by(user_id=user.id).first()
    return render_template('profile.html', user=user, formulir=formulir)

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

# Add this at the bottom of the file, just before the if __name__ == '__main__': block
def create_admin():
    # Check if admin exists
    admin = User.query.filter_by(username='admin@admin.com').first()
    if not admin:
        # Create admin user
        admin_password = generate_password_hash('admin123')
        admin = User(username='admin@admin.com', 
                    password=admin_password,
                    is_admin=True,
                    is_verified=True)
        db.session.add(admin)
        db.session.commit()

@app.context_processor
def utility_processor():
    def get_current_user():
        if 'user_id' in session:
            return User.query.get(session['user_id'])
        return None
        
    def get_user_formulir():
        if 'user_id' in session:
            return Formulir.query.filter_by(user_id=session['user_id']).first()
        return None
        
    return dict(get_current_user=get_current_user, get_user_formulir=get_user_formulir)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('static/uploads', filename)  # Update path to match folder structure

@app.route('/pembayaran', methods=['GET', 'POST'])
@login_required
def pembayaran():
    user = User.query.get(session['user_id'])
    formulir = Formulir.query.filter_by(user_id=user.id).first()

    if not formulir or formulir.verifikasi_status != 'approved':
        flash('Anda harus disetujui terlebih dahulu sebelum melakukan pembayaran.')
        return redirect(url_for('profile'))

    if request.method == 'POST':
        if 'pembayaran' in request.files:
            pembayaran = request.files['pembayaran']
            if pembayaran:
                pembayaran_filename = secure_filename(pembayaran.filename)
                pembayaran.save(os.path.join(app.config['UPLOAD_FOLDER'], pembayaran_filename))
                formulir.pembayaran_path = 'uploads/' + pembayaran_filename
                formulir.pembayaran_status = 'pending'
                db.session.commit()
                flash('Bukti pembayaran berhasil diunggah dan sedang diverifikasi.')
                return redirect(url_for('profile'))

    return render_template('pembayaran.html', user=user, formulir=formulir)

@app.route('/admin/verifikasi_pembayaran/<int:user_id>/<action>')
@admin_login_required
def verifikasi_pembayaran(user_id, action):
    formulir = Formulir.query.filter_by(user_id=user_id).first()
    
    if not formulir:
        flash('Formulir tidak ditemukan.')
        return redirect(url_for('admin_verifikasi_list'))

    if action == 'terima':
        formulir.pembayaran_status = 'approved'
    elif action == 'tolak':
        formulir.pembayaran_status = 'rejected'

    db.session.commit()
    flash(f'Status pembayaran berhasil diperbarui.')
    return redirect(url_for('admin_verifikasi_list'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
<<<<<<< HEAD
    app.run(debug=True, host='0.0.0.0')
=======
    app.run(debug=True, host='0,0,0,0')
>>>>>>> e4bc1f119402f65a917ec570ad3747e1134666ab
