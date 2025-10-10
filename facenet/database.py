import os
from flask_sqlalchemy import SQLAlchemy

# Create database folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "data", "database")
os.makedirs(DB_DIR, exist_ok=True)

db_path = os.path.join(DB_DIR, "student_attendance.db")
db = SQLAlchemy()

class Attendance(db.Model):
        __tablename__ = "attendance"
        id = db.Column(db.Integer, primary_key=True)
        student = db.Column(db.String(120), nullable=False)
        date = db.Column(db.String(10), nullable=False)
        intime = db.Column(db.String(50))
        outtime = db.Column(db.String(50))
        __table_args__ = (db.UniqueConstraint('student', 'date', name='uix_name_date'),)

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(120))
    embedding = db.Column(db.PickleType, nullable=False)

def init_db(app):
    """Initialize the database and return db and Attendance model"""
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    

    with app.app_context():
        db.create_all()

    return db, Attendance, Student
