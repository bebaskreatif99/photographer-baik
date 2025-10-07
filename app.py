import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (Flask, render_template, url_for, flash, 
                   redirect, request, session, abort)
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form.upload import ImageUploadField
from wtforms import TextAreaField
from wtforms.widgets import TextArea

# -- Inisialisasi Aplikasi dan Konfigurasi --
app = Flask(__name__)

# Konfigurasi penting: Ganti 'your_super_secret_key_change_me' dengan kunci acak yang kuat.
# Sebaiknya gunakan environment variable di lingkungan produksi.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# -- Konfigurasi Path untuk Upload Gambar --
UPLOAD_FOLDER_ROOT = os.path.join(app.root_path, 'static', 'uploads')
PHOTO_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER_ROOT, 'gallery_images')
BLOG_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER_ROOT, 'blog_images')
HERO_UPLOAD_FOLDER = os.path.join(UPLOAD_FOLDER_ROOT, 'hero_images')

# Buat direktori jika belum ada
for folder in [PHOTO_UPLOAD_FOLDER, BLOG_UPLOAD_FOLDER, HERO_UPLOAD_FOLDER]:
    os.makedirs(folder, exist_ok=True)

PHOTO_URL_RELATIVE = 'uploads/gallery_images/'
BLOG_URL_RELATIVE = 'uploads/blog_images/'
HERO_URL_RELATIVE = 'uploads/hero_images' # Hapus garis miring di akhir


# -- Models Database --
class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<AdminUser {self.username}>'

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    is_featured = db.Column(db.Boolean, default=False, index=True)
    date_uploaded = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Photo {self.filename}>'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    thumbnail_filename = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Blog {self.title}>'

class HeroSlide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subtitle = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(255), unique=True, nullable=False)
    order_num = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True, index=True)
    cta_text = db.Column(db.String(100), default='Lihat Portofolio')
    cta_url = db.Column(db.String(255), default='/gallery')

    def __repr__(self):
        return f'<HeroSlide {self.title}>'

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True) # prewedding, wedding, event
    features = db.Column(db.Text, nullable=False) # Fitur dipisahkan dengan baris baru
    order_num = db.Column(db.Integer, default=0)

    def get_features_list(self):
        return [feature.strip() for feature in self.features.splitlines() if feature.strip()]

    def __repr__(self):
        return f'<Package {self.name}>'


# -- Fungsi Helper --
def _custom_filename(field, file_data):
    ext = os.path.splitext(file_data.filename)[1]
    base_filename = secure_filename(os.path.splitext(file_data.filename)[0])
    unique_filename = f"{uuid.uuid4().hex[:16]}_{base_filename}{ext}"
    return unique_filename

# -- Konfigurasi Panel Admin yang Aman --
class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super().__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class SecureModelView(ModelView):
    def is_accessible(self):
        return session.get('is_admin')

    def inaccessible_callback(self, name, **kwargs):
        flash('Anda harus login untuk mengakses halaman ini.', 'error')
        return redirect(url_for('login'))

class CustomAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not session.get('is_admin'):
            return redirect(url_for('login'))
        
        stats = {
            'photo_count': db.session.query(Photo).count(),
            'blog_count': db.session.query(Blog).count(),
            'hero_slide_count': HeroSlide.query.filter_by(is_active=True).count(),
            'package_count': db.session.query(Package).count()
        }
        return self.render('admin/index.html', **stats)

admin = Admin(app, name='Photographer.Baik Admin', template_mode='bootstrap4', index_view=CustomAdminIndexView())

class PhotoAdminView(SecureModelView):
    column_list = ('filename', 'category', 'is_featured', 'date_uploaded')
    column_filters = ('category', 'is_featured')
    column_editable_list = ('category', 'is_featured')
    form_columns = ('filename', 'category', 'description', 'is_featured')

    def _list_thumbnail(view, context, model, name):
        if not model.filename: return ''
        url = url_for("static", filename=PHOTO_URL_RELATIVE + model.filename)
        return Markup(f'<img src="{url}" style="width: 100px; height: auto; border-radius: 4px;">')
    
    column_formatters = {'filename': _list_thumbnail}

    form_extra_fields = {
        'filename': ImageUploadField('Upload Gambar',
            base_path=PHOTO_UPLOAD_FOLDER,
            url_relative_path=PHOTO_URL_RELATIVE,
            namegen=_custom_filename,
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'],
            max_size=(3840, 3840, True),
            thumbnail_size=(100, 100, True))
    }

class BlogAdminView(SecureModelView):
    column_list = ('title', 'author', 'category', 'created_at')
    column_filters = ('category', 'author')
    form_overrides = {'content': CKTextAreaField}
    
    form_columns = ('title', 'slug', 'author', 'category', 'thumbnail_filename', 'content')
    
    def on_model_change(self, form, model, is_created):
        if not model.slug:
            model.slug = form.title.data.lower().replace(' ', '-')
        super().on_model_change(form, model, is_created)

    form_extra_fields = {
        'thumbnail_filename': ImageUploadField('Gambar Thumbnail',
            base_path=BLOG_UPLOAD_FOLDER,
            url_relative_path=BLOG_URL_RELATIVE,
            namegen=_custom_filename,
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
    }

class HeroSlideAdminView(SecureModelView):
    column_list = ('title', 'order_num', 'is_active', 'image_filename')
    column_editable_list = ('order_num', 'is_active')
    
    def _list_thumbnail(view, context, model, name):
        if not model.image_filename: return ''
        url = url_for("static", filename=HERO_URL_RELATIVE + model.image_filename)
        return Markup(f'<img src="{url}" style="width: 150px; height: auto;">')
    
    column_formatters = {'image_filename': _list_thumbnail}
    
    form_extra_fields = {
        'image_filename': ImageUploadField('Gambar Slide',
            base_path=HERO_UPLOAD_FOLDER,
            url_relative_path=HERO_URL_RELATIVE,
            namegen=_custom_filename,
            allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])
    }

class PackageAdminView(SecureModelView):
    column_list = ('name', 'category', 'price', 'order_num')
    column_filters = ('category',)
    column_editable_list = ('price', 'order_num')
    form_columns = ('name', 'category', 'price', 'order_num', 'features')
    form_widget_args = {
        'features': {
            'rows': 10,
            'placeholder': 'Masukkan satu fitur per baris...'
        }
    }

admin.add_view(PhotoAdminView(Photo, db.session, name='Galeri Foto', category='Konten'))
admin.add_view(BlogAdminView(Blog, db.session, name='Artikel Blog', category='Konten'))
admin.add_view(HeroSlideAdminView(HeroSlide, db.session, name='Slide Hero', category='Tampilan'))
admin.add_view(PackageAdminView(Package, db.session, name='Paket Layanan', category='Tampilan'))

# -- Routes untuk Autentikasi Admin --
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('is_admin'):
        return redirect('/admin')
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = AdminUser.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['is_admin'] = True
            session['username'] = user.username
            flash('Login berhasil!', 'success')
            return redirect('/admin')
        else:
            flash('Username atau password salah.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('login'))

# -- Routes untuk Frontend --
@app.route('/')
def index():
    hero_slides = HeroSlide.query.filter_by(is_active=True).order_by(HeroSlide.order_num.asc()).all()
    featured_photos = Photo.query.filter_by(is_featured=True).order_by(Photo.date_uploaded.desc()).limit(6).all()
    recent_posts = Blog.query.order_by(Blog.created_at.desc()).limit(3).all()
    return render_template('index.html', hero_slides=hero_slides, featured_photos=featured_photos, recent_posts=recent_posts)

@app.route('/about')
def about():
    return render_template('about.html', title='Tentang Kami')

@app.route('/gallery')
def gallery():
    selected_category = request.args.get('category', 'All')
    
    if selected_category == 'All':
        photos = Photo.query.order_by(Photo.date_uploaded.desc()).all()
    else:
        photos = Photo.query.filter_by(category=selected_category).order_by(Photo.date_uploaded.desc()).all()
        
    categories = db.session.query(Photo.category).distinct().all()
    categories = sorted([c[0] for c in categories])
    
    return render_template('gallery.html', title='Galeri', photos=photos, categories=categories, selected_category=selected_category)

@app.route('/packages/<category_name>')
def packages(category_name):
    valid_categories = ['prewedding', 'wedding', 'event']
    if category_name not in valid_categories:
        abort(404)
    
    package_list = Package.query.filter(Package.category.ilike(category_name)).order_by(Package.order_num.asc()).all()
    title = f"Paket {category_name.capitalize()}"
    return render_template('packages.html', title=title, packages=package_list, category_name=category_name)

@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts = Blog.query.order_by(Blog.created_at.desc()).paginate(page=page, per_page=6)
    return render_template('blog.html', title='Blog', posts=posts)

@app.route('/blog/<string:slug>')
def post_detail(slug):
    post = Blog.query.filter_by(slug=slug).first_or_404()
    return render_template('post_detail.html', title=post.title, post=post)

# -- Error Handler dan Context Processor --
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.context_processor
def inject_global_data():
    return {
        'PHOTO_URL_RELATIVE': PHOTO_URL_RELATIVE,
        'BLOG_URL_RELATIVE': BLOG_URL_RELATIVE,
        'HERO_URL_RELATIVE': HERO_URL_RELATIVE
    }

# -- CLI Commands untuk Manajemen Admin --
@app.cli.command("create-admin")
def create_admin():
    """Membuat user admin baru."""
    username = input("Masukkan username admin: ")
    password = input("Masukkan password admin: ")
    
    if AdminUser.query.filter_by(username=username).first():
        print(f"User '{username}' sudah ada.")
        return
        
    new_admin = AdminUser(username=username)
    new_admin.set_password(password)
    db.session.add(new_admin)
    db.session.commit()
    print(f"User admin '{username}' berhasil dibuat.")

@app.cli.command("update-admin-password")
def update_admin_password():
    """Mengganti password user admin."""
    username = input("Masukkan username admin yang ingin diganti passwordnya: ")
    user = AdminUser.query.filter_by(username=username).first()
    
    if not user:
        print(f"Error: User dengan username '{username}' tidak ditemukan.")
        return
        
    new_password = input(f"Masukkan password baru untuk {username}: ")
    user.set_password(new_password)
    db.session.commit()
    print(f"Password untuk admin '{username}' berhasil diperbarui.")

@app.cli.command("update-admin-username")
def update_admin_username():
    """Mengganti username user admin."""
    old_username = input("Masukkan username LAMA: ")
    user = AdminUser.query.filter_by(username=old_username).first()

    if not user:
        print(f"Error: User dengan username '{old_username}' tidak ditemukan.")
        return

    new_username = input("Masukkan username BARU: ")
    if AdminUser.query.filter_by(username=new_username).first():
        print(f"Error: Username '{new_username}' sudah digunakan oleh user lain.")
        return

    user.username = new_username
    db.session.commit()
    print(f"Username '{old_username}' berhasil diubah menjadi '{new_username}'.")


if __name__ == '__main__':
    # Set debug=False saat aplikasi sudah online (di tahap produksi)
    app.run(debug=True)