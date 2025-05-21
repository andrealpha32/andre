from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import os
import json
from functools import lru_cache
from datetime import timedelta, datetime
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
    posts = db.relationship('ForumPost', backref='author', lazy=True)
    comments = db.relationship('ForumComment', backref='author', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

  
class Formulir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='formulir')

    # Data diri yang akan disimpan di Formulir
    nama_lengkap = db.Column(db.String(100))
    tempat_lahir = db.Column(db.String(100))
    tanggal_lahir = db.Column(db.String(100))
    jenis_kelamin = db.Column(db.String(20))
    alamat = db.Column(db.String(200))
    asal_sekolah = db.Column(db.String(200))
    jurusan = db.Column(db.String(100))
    no_hp = db.Column(db.String(20))
    
    foto_path = db.Column(db.String(200))
    ijazah_path = db.Column(db.String(200))
    pembayaran_path = db.Column(db.String(200))
    pembayaran_status = db.Column(db.String(20), default='belum')
    verifikasi_status = db.Column(db.String(20), default='belum')

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    formulir_id = db.Column(db.Integer, db.ForeignKey('formulir.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    verification_timestamp = db.Column(db.DateTime)
    rejection_reason = db.Column(db.String(200))

    user = db.relationship('User')
    formulir = db.relationship('Formulir')

class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    comments = db.relationship('ForumComment', backref='post', lazy=True, cascade='all, delete-orphan')

class ForumComment(db.Model):
    __tablename__ = 'forum_comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)

class OnlineUser(db.Model):
    __tablename__ = 'online_users'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User')

class OrientationSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer)
    date = db.Column(db.String(100))
    time = db.Column(db.String(100))
    activity = db.Column(db.String(200))
    location = db.Column(db.String(200))

class OrientationMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(200), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=db.func.now())

class WhatsAppGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_grup = db.Column(db.String(200), nullable=False)
    jurusan = db.Column(db.String(100), nullable=False)
    link_grup = db.Column(db.String(500), nullable=False)
    deskripsi = db.Column(db.Text, nullable=False)
    
# Configure upload folder
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.before_request
def make_session_permanent():
    session.permanent = True

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Anda perlu masuk terlebih dahulu.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

def admin_login_required(f):
    def wrapper(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Anda perlu login sebagai admin terlebih dahulu.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

@app.before_request
def update_last_seen():
    if 'user_id' in session:
        # Update or create online status
        online_user = OnlineUser.query.filter_by(user_id=session['user_id']).first()
        if online_user:
            online_user.last_seen = datetime.utcnow()
        else:
            online_user = OnlineUser(user_id=session['user_id'])
            db.session.add(online_user)
        db.session.commit()

        # Clean up old sessions (older than 5 minutes)
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        OnlineUser.query.filter(OnlineUser.last_seen < five_minutes_ago).delete()
        db.session.commit()

@app.route('/admin_dashboard', endpoint="admin_dashboard_view")
@admin_login_required
def admin_dashboard():
    # Get all formulir data
    all_formulir = Formulir.query.all()
    total_pendaftar = len(all_formulir)
    
    # Status statistics
    diterima = Formulir.query.filter_by(verifikasi_status='approved').count()
    ditolak = Formulir.query.filter_by(verifikasi_status='rejected').count()
    pending = Formulir.query.filter_by(verifikasi_status='pending').count()
    
    # Jurusan statistics
    jurusan_counts = {}
    for formulir in all_formulir:
        if formulir.jurusan:
            jurusan_counts[formulir.jurusan] = jurusan_counts.get(formulir.jurusan, 0) + 1
    
    # Payment statistics
    pembayaran_diterima = Formulir.query.filter_by(pembayaran_status='approved').count()
    pembayaran_pending = Formulir.query.filter_by(pembayaran_status='pending').count()
    pembayaran_ditolak = Formulir.query.filter_by(pembayaran_status='rejected').count()
    
    # Recent registrations (last 5)
    recent_registrations = Formulir.query.order_by(Formulir.id.desc()).limit(5).all()

    return render_template('admin_dashboard.html',
                         total_pendaftar=total_pendaftar,
                         diterima=diterima,
                         ditolak=ditolak,
                         pending=pending,
                         jurusan_counts=jurusan_counts,
                         pembayaran_diterima=pembayaran_diterima,
                         pembayaran_pending=pembayaran_pending,
                         pembayaran_ditolak=pembayaran_ditolak,
                         recent_registrations=recent_registrations)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.is_admin and check_password_hash(user.password, password):
            session['admin_logged_in'] = True
            session['user_id'] = user.id
            flash('Login admin berhasil.')
            return redirect(url_for('admin_dashboard_view'))  # Change this line to use correct endpoint
        else:
            if not user:
                flash('Username tidak ditemukan.')
            elif not user.is_admin:
                flash('Akun ini bukan admin.')
            else:
                flash('Password salah.')
                
    return render_template('admin_login.html')

@app.route('/admin_logout')
def admin_logout():
    # Clear all session data for admin
    session.clear()
    flash('Anda telah berhasil logout sebagai admin.')
    return redirect(url_for('admin_login'))

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

@app.route('/verifikasi', methods=['GET', 'POST'])
@login_required
def verifikasi():
    user = User.query.get(session.get('user_id'))
    if not user:
        flash("User tidak ditemukan. Silakan login ulang.")
        return redirect(url_for('logout'))

    formulir = Formulir.query.filter_by(user_id=user.id).first()
    
    if not formulir and request.method == 'GET':
        formulir = Formulir(user_id=user.id)
        db.session.add(formulir)
        db.session.commit()

    if request.method == 'POST':
        if not formulir:
            formulir = Formulir(user_id=user.id)

        # Update formulir data
        formulir.nama_lengkap = request.form['nama_lengkap']
        formulir.tempat_lahir = request.form['tempat_lahir']
        formulir.tanggal_lahir = request.form['tanggal_lahir']
        formulir.jenis_kelamin = request.form['jenis_kelamin']
        formulir.alamat = request.form['alamat']
        formulir.asal_sekolah = request.form['asal_sekolah']
        formulir.jurusan = request.form['jurusan']
        formulir.no_hp = request.form['no_hp']
        formulir.verifikasi_status = 'pending'

        # Handle file uploads
        for field in ['foto', 'ijazah', 'pembayaran']:
            if field in request.files:
                file = request.files[field]
                if file:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    setattr(formulir, f'{field}_path', f'uploads/{filename}')

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
            # Validasi format emailil
            validate_email(username)

            # Validasi panjang password
            if len(password) < 8:
                flash('Password harus minimal 8 karakter.')
                return render_template('register.html')

            if User.query.filter_by(username=username).first():
                flash('Username sudah ada. Silakan pilih yang lain.')
            else:
                hashed_password = generate_password_hash(password)
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

    # Get statistics for dashboard
    total_pendaftar = Formulir.query.count()
    verified_count = Formulir.query.filter_by(verifikasi_status='approved').count()
    pending_count = Formulir.query.filter_by(verifikasi_status='pending').count()

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

    return render_template('index.html', 
                         user=user, 
                         formulir=formulir, 
                         pesan=pesan,
                         total_pendaftar=total_pendaftar,
                         verified_count=verified_count,
                         pending_count=pending_count)

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
    return send_from_directory('static/uploads', filename)

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

@app.route('/admin/payments')
@admin_login_required
def admin_payment_list():
    payments = db.session.query(Payment).join(Formulir).order_by(Payment.timestamp.desc()).all()
    return render_template('admin_payment_verification.html', payments=payments)

@app.route('/admin/verify-payment/<int:id>', methods=['POST'])
@admin_login_required
def admin_verify_payment(id):
    payment = Payment.query.get_or_404(id)
    payment.status = 'approved'
    payment.verification_timestamp = datetime.now()
    
    # Update formulir payment status
    formulir = payment.formulir
    formulir.pembayaran_status = 'approved'
    formulir.pembayaran_timestamp = datetime.now()
    
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/reject-payment/<int:id>', methods=['POST'])
@admin_login_required
def admin_reject_payment(id):
    data = request.get_json()
    if not data or 'reason' not in data:
        return jsonify({'error': 'Reason is required'}), 400
        
    payment = Payment.query.get_or_404(id)
    payment.status = 'rejected'
    payment.rejection_reason = data['reason']
    payment.verification_timestamp = datetime.now()
    
    # Update formulir payment status
    formulir = payment.formulir
    formulir.pembayaran_status = 'rejected'
    formulir.pembayaran_timestamp = datetime.now()
    
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/admin/schedule', methods=['GET', 'POST'])
@admin_login_required
def admin_schedule():
    if request.method == 'POST':
        day = request.form.get('day')
        date = request.form.get('date')
        time = request.form.get('time')
        activity = request.form.get('activity')
        location = request.form.get('location')
        
        schedule = OrientationSchedule(
            day=day,
            date=date,
            time=time, 
            activity=activity,
            location=location
        )
        db.session.add(schedule)
        db.session.commit()
        
        flash('Jadwal berhasil ditambahkan')
        return redirect(url_for('admin_schedule'))
        
    schedules = OrientationSchedule.query.order_by(OrientationSchedule.day, OrientationSchedule.time).all()
    return render_template('admin/schedule.html', schedules=schedules)

@app.route('/admin/schedule/delete/<int:id>')
@admin_login_required
def delete_schedule(id):
    schedule = OrientationSchedule.query.get_or_404(id)
    db.session.delete(schedule)
    db.session.commit()
    flash('Jadwal berhasil dihapus')
    return redirect(url_for('admin_schedule'))

@app.route('/admin/materi', methods=['GET'])
@admin_login_required
def admin_materi():
    materi = OrientationMaterial.query.all()
    return render_template('admin/materi.html', materi=materi)

@app.route('/admin/materi/add', methods=['POST'])
@admin_login_required
def admin_add_materi():
    judul = request.form.get('judul')
    deskripsi = request.form.get('deskripsi')
    icon = request.form.get('icon')
    file = request.files.get('file')
    
    if not all([judul, deskripsi, icon]):
        flash('Semua field harus diisi', 'error')
        return redirect(url_for('admin_materi'))
    
    file_path = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join('uploads', filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('File harus berformat PDF', 'error')
            return redirect(url_for('admin_materi'))
    
    materi = OrientationMaterial(
        judul=judul,
        deskripsi=deskripsi,
        icon=icon,
        file_path=file_path
    )
    db.session.add(materi)
    db.session.commit()
    
    flash('Materi berhasil ditambahkan', 'success')
    return redirect(url_for('admin_materi'))

@app.route('/admin/materi/delete/<int:id>', methods=['POST'])
@admin_login_required
def admin_delete_materi(id):
    try:
        materi = OrientationMaterial.query.get_or_404(id)
        if materi.file_path:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], materi.file_path.split('/')[-1]))
            except:
                pass
        db.session.delete(materi)
        db.session.commit()
        flash('Materi berhasil dihapus', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
    
    return redirect(url_for('admin_materi'))

# Admin management routes
@app.route('/admin/jadwal', methods=['GET', 'POST'])
@admin_login_required
def admin_jadwal():
    jadwal = OrientationSchedule.query.order_by(OrientationSchedule.day, OrientationSchedule.time).all()
    return render_template('admin/jadwal.html', jadwal=jadwal)

@app.route('/admin/jadwal/add', methods=['POST'])
@admin_login_required
def admin_add_jadwal():
    try:
        day = int(request.form.get('day'))
        date = request.form.get('date')
        time = request.form.get('time')
        activity = request.form.get('activity')
        location = request.form.get('location')
        
        if not all([day, date, time, activity, location]):
            flash('Semua field harus diisi', 'error')
            return redirect(url_for('admin_jadwal'))
        
        jadwal = OrientationSchedule(
            day=day,
            date=date,
            time=time,
            activity=activity,
            location=location
        )
        db.session.add(jadwal)
        db.session.commit()
        
        flash('Jadwal berhasil ditambahkan', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
    
    return redirect(url_for('admin_jadwal'))

@app.route('/admin/jadwal/delete/<int:id>', methods=['POST'])
@admin_login_required
def admin_delete_jadwal(id):
    try:
        jadwal = OrientationSchedule.query.get_or_404(id)
        db.session.delete(jadwal)
        db.session.commit()
        flash('Jadwal berhasil dihapus', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
    
    return redirect(url_for('admin_jadwal'))

@app.route('/admin/grup', methods=['GET'])
@admin_login_required
def admin_grup():
    grup = WhatsAppGroup.query.all()
    return render_template('admin/grup.html', grup=grup)

@app.route('/admin/grup/add', methods=['POST'])
@admin_login_required
def admin_add_grup():
    try:
        nama_grup = request.form.get('nama_grup')
        jurusan = request.form.get('jurusan')
        link_grup = request.form.get('link_grup')
        deskripsi = request.form.get('deskripsi')
        
        if not all([nama_grup, jurusan, link_grup, deskripsi]):
            flash('Semua field harus diisi', 'error')
            return redirect(url_for('admin_grup'))
            
        grup = WhatsAppGroup(
            nama_grup=nama_grup,
            jurusan=jurusan, 
            link_grup=link_grup,
            deskripsi=deskripsi
        )
        db.session.add(grup)
        db.session.commit()
        
        flash('Grup WhatsApp berhasil ditambahkan', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
    
    return redirect(url_for('admin_grup'))

@app.route('/admin/grup/delete/<int:id>', methods=['POST'])
@admin_login_required
def admin_delete_grup(id):
    try:
        grup = WhatsAppGroup.query.get_or_404(id)
        db.session.delete(grup)
        db.session.commit()
        flash('Grup WhatsApp berhasil dihapus', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Terjadi kesalahan: {str(e)}', 'error')
    
    return redirect(url_for('admin_grup'))

@app.route('/grup-wa')
@login_required
def grup_wa():
    formulir = Formulir.query.filter_by(user_id=session['user_id']).first()
    if not formulir or formulir.pembayaran_status != 'approved':
        flash('Anda harus menyelesaikan pembayaran terlebih dahulu')
        return redirect(url_for('index'))
    
    grup = WhatsAppGroup.query.all()
    return render_template('orientasi/grup.html', grup=grup, formulir=formulir)

@app.route('/forum-siswa')
@login_required
def forum_siswa():
    formulir = Formulir.query.filter_by(user_id=session['user_id']).first()
    if not formulir or formulir.pembayaran_status != 'approved':
        flash('Anda harus menyelesaikan pembayaran terlebih dahulu')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    # Get online users
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    online_users = User.query.join(OnlineUser).filter(OnlineUser.last_seen >= five_minutes_ago).all()
    
    # Convert posts to dictionary for JSON serialization
    posts = ForumPost.query.order_by(ForumPost.timestamp.desc()).all()
    posts_data = []
    for post in posts:
        # Convert datetime to ISO format string
        post_dict = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'timestamp': post.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
            'likes': post.likes,
            'author': {'username': post.author.username},
            'comments': [{
                'content': c.content,
                'timestamp': c.timestamp.strftime('%Y-%m-%dT%H:%M:%S'),
                'author': {'username': c.author.username}
            } for c in post.comments]
        }
        posts_data.append(post_dict)
    
    return render_template('orientasi/forum.html', 
                         posts=posts_data, 
                         user=user,
                         online_users=online_users)

@app.route('/forum/post', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not content:
        flash('Judul dan konten harus diisi')
        return redirect(url_for('forum_siswa'))
        
    post = ForumPost(title=title, content=content, user_id=session['user_id'])
    db.session.add(post)
    db.session.commit()
    
    flash('Post berhasil dibuat')
    return redirect(url_for('forum_siswa'))

@app.route('/forum/comment/<int:post_id>', methods=['POST'])
@login_required
def create_comment(post_id):
    content = request.form.get('content')
    
    if not content:
        flash('Komentar tidak boleh kosong')
        return redirect(url_for('forum_siswa'))
        
    comment = ForumComment(content=content, user_id=session['user_id'], post_id=post_id)
    db.session.add(comment)
    db.session.commit()
    
    flash('Komentar berhasil ditambahkan')
    return redirect(url_for('forum_siswa'))

@app.route('/forum/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})

@app.route('/jadwal-orientasi')
@login_required
def jadwal_orientasi():
    formulir = Formulir.query.filter_by(user_id=session['user_id']).first()
    if not formulir or formulir.pembayaran_status != 'approved':
        flash('Anda harus menyelesaikan pembayaran terlebih dahulu')
        return redirect(url_for('index'))
    
    schedules = OrientationSchedule.query.order_by(OrientationSchedule.day, OrientationSchedule.time).all()
    return render_template('orientasi/jadwal.html', schedules=schedules)

@app.route('/materi-persiapan')
@login_required
def materi_persiapan():
    formulir = Formulir.query.filter_by(user_id=session['user_id']).first()
    if not formulir or formulir.pembayaran_status != 'approved':
        flash('Anda harus menyelesaikan pembayaran terlebih dahulu')
        return redirect(url_for('index'))
    
    materi = OrientationMaterial.query.all()
    return render_template('orientasi/materi.html', materi=materi)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin()
    app.run(debug=True, host='0.0.0.0')
