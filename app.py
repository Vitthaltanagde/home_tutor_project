from flask import Flask, render_template, request, redirect, url_for,session, flash , Response 
from flask_sqlalchemy import SQLAlchemy
# from insert_pincode_data import pincodes
import os
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import random

app = Flask(__name__)

app.secret_key = 'your_secret_key'
# Configure Database
basedir = os.path.abspath("C:/vitthal_folder/home_tutor_project")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'tutorfinder.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ========================
# Database Models
# ========================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    grade = db.Column(db.Integer)
    mode = db.Column(db.String(50))
    board = db.Column(db.String(50))
    city = db.Column(db.String(100))
    address = db.Column(db.String(200))
    contact = db.Column(db.String(20))

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    course = db.Column(db.String(100))
    board = db.Column(db.String(50))
    subjects = db.Column(db.String(200))

class PincodeLocation(db.Model): 
    __tablename__ = 'pincode_locations'

    id = db.Column(db.Integer, primary_key=True)
    pincode = db.Column(db.String(6), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"{self.location} - {self.pincode}"


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) 


# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'  # Use Gmail App Password

mail = Mail(app)

# Only this email is allowed for admin access
ADMIN_EMAIL = 'admin@example.com'

# ========================
# Routes
# ========================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup-student', methods=['GET', 'POST'])
def signup_student():
    if request.method == 'POST':
        student = Student(
            name=request.form['name'],
            grade=request.form['grade'],
            mode=request.form['mode'],
            board=request.form['board'],
            city=request.form['city'],
            address=request.form['address'],
            contact=request.form['contact']
        )
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('home'))

    # Fetch pincode locations from DB
    locations = PincodeLocation.query.order_by(PincodeLocation.location).all()
    return render_template('signup_student.html', locations=locations)

@app.route('/signup-tutor', methods=['GET', 'POST'])
def signup_tutor():
    if request.method == 'POST':
        subjects = ', '.join(request.form.getlist('subjects'))
        tutor = Tutor(
            name=request.form['name'],
            mobile=request.form['mobile'],
            email=request.form['email'],
            course=request.form['course'],
            board=request.form['board'],
            subjects=subjects
        )
        db.session.add(tutor)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('signup_tutor.html')

@app.route('/student-dashboard')
def student_dashboard():
    tutors = Tutor.query.all()
    return render_template('student_dashboard.html', tutors=tutors)

@app.route('/tutor-dashboard')
def tutor_dashboard():
    students = Student.query.all()
    return render_template('tutor_dashboard.html', students=students)

@app.route('/otp-login', methods=['GET'])
def otp_login():
    return render_template('otp_login.html', show_otp_form=False)

@app.route('/send-otp', methods=['POST'])
def send_otp():
    email = request.form['email']
    if email != ADMIN_EMAIL:
        flash('Unauthorized email', 'error')
        return redirect(url_for('otp_login'))

    otp = str(random.randint(100000, 999999))
    session['otp'] = otp
    session['email'] = email

    msg = Message("Your OTP for Admin Login", sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f"Your OTP is: {otp}"
    mail.send(msg)

    return render_template('otp_login.html', show_otp_form=True, email=email)

@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    user_otp = request.form['otp']
    email = request.form['email']

    if user_otp == session.get('otp') and email == session.get('email'):
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid OTP', 'error')
        return redirect(url_for('otp_login'))

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('otp_login'))
    return "Welcome to Admin Dashboard"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('otp_login'))










if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates all tables
    app.run(debug=True)
