# test_admin.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

# Konfigurasi aplikasi dasar
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-for-testing'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

# Model database sederhana untuk tes
class TestModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

# Inisialisasi Admin dengan bootstrap4
admin = Admin(app, name='Test Admin Panel', template_mode='bootstrap4')
admin.add_view(ModelView(TestModel, db.session))

# Membuat database saat aplikasi dijalankan
with app.app_context():
    db.create_all()

# Menjalankan aplikasi di port yang berbeda (5001)
if __name__ == '__main__':
    app.run(debug=True, port=5001)