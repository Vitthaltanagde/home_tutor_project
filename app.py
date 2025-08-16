from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from flask_sitemap import Sitemap
import requests
import pandas as pd
from flask import send_file

app = Flask(__name__)
app.secret_key = 'your_secret_key'
ext = Sitemap(app=app)

# Configure Database
basedir = os.path.abspath("C:/vitthal_folder/home_tutor_project")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pass2123@localhost/home_tutor'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Telegram Bot
TELEGRAM_BOT_TOKEN = "8347698502:AAE3E09O7QaCdw14Gwb-k6H_jIBuaYo_NWQ"
TELEGRAM_CHAT_ID = "-1002691110187"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram Error:", e)

# ========================
# Database Models
# ========================

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    grade = db.Column(db.String(100))
    mode = db.Column(db.String(50))
    board = db.Column(db.String(50))
    address = db.Column(db.String(200))
    contact = db.Column(db.String(20))
    description = db.Column(db.Text)
    teacher_gender = db.Column(db.String(20))

class Tutor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(100))
    experience = db.Column(db.String(100))
    course = db.Column(db.String(100))
    gender = db.Column(db.String(100))
    board = db.Column(db.String(50))
    subjects = db.Column(db.String(200))
    # image_filename = db.Column(db.String(200), nullable=True)
    # rating = db.Column(db.Float, default=4.8)
    # reviews_count = db.Column(db.Integer, default=25)

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
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# ========================
# Routes
# ========================

@app.route('/')
def home():
    return render_template(
        'index.html',
        title="GuruGO - Find Best Home Tutors in Pune",
        description="GuruGO connects you with expert tutors in Pune for CBSE, ICSE, SSC, HSC & competitive exams. Book your tutor today!",
        keywords="home tutor Pune, CBSE tuition Pune, ICSE coaching, SSC tutor Pune, HSC classes Pune"
    )

@app.route('/tutor/<int:tutor_id>')
def tutor_profile(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    return render_template(
        'tutor_profile.html',
        title=f"{tutor.name} - {tutor.subjects} Tutor in Pune | GuruGO",
        description=f"Book {tutor.name}, an experienced {tutor.subjects} tutor in Pune with {tutor.experience} years of teaching experience.",
        keywords=f"{tutor.subjects} tutor Pune, {tutor.board} coaching, private tuition Pune",
        tutor=tutor,
        rating_value=tutor.rating,
        review_count=tutor.reviews_count
    )

@app.route('/signup-student', methods=['GET', 'POST'])
def signup_student():
    if request.method == 'POST':
        selected_grades = request.form.getlist('grade')
        grades_str = ', '.join(selected_grades)

        student = Student(
            name=request.form['name'],
            grade=grades_str,
            mode=request.form['mode'],
            board=request.form['board'],
            address=request.form['address'],
            contact=request.form['contact'],
            description=request.form['description'],
            teacher_gender=request.form['teacher_gender']
        )
        db.session.add(student)
        db.session.commit()

        message = (
            "🎓 *New Student Signup*\n\n"
            f"👤 Name: {student.name}\n"
            f"📚 Grade(s): {grades_str}\n"
            f"🏫 Mode: {student.mode}\n"
            f"📋 Board: {student.board}\n"
            f"📍 Address: {student.address}\n"
            f"📞 Contact: {student.contact}\n"
            f"📝 Description: {student.description}\n"
            f"🙋‍♂️ Preferred Teacher Gender: {student.teacher_gender}"
        )
        send_telegram_message(message)

        session['show_popup'] = True
        session['student_name'] = student.name

        return redirect(url_for('welcome'))

    return render_template('signup_student.html')

@app.route('/signup-tutor', methods=['GET', 'POST'])
def signup_tutor():
    if request.method == 'POST':
        subjects = ', '.join(request.form.getlist('subjects'))
        board = ', '.join(request.form.getlist('board'))

        tutor = Tutor(
            name=request.form['name'],
            mobile=request.form['mobile'],
            email=request.form['email'],
            experience=request.form['experience'],
            course=request.form['course'],
            gender=request.form['gender'],
            board=board,
            subjects=subjects
        )
        db.session.add(tutor)
        db.session.commit()

        message = (
            "👨‍🏫 *New Tutor Signup*\n\n"
            f"👤 Name: {tutor.name}\n"
            f"📞 Mobile: {tutor.mobile}\n"
            f"📧 Email: {tutor.email}\n"
            f"💼 Experience: {tutor.experience}\n"
            f"📚 Course: {tutor.course}\n"
            f"⚧ Gender: {tutor.gender}\n"
            f"📋 Board(s): {board}\n"
            f"📖 Subjects: {subjects}"
        )
        send_telegram_message(message)

        session['show_popup'] = True
        session['tutor_name'] = tutor.name

        return redirect(url_for('welcome_tutor'))

    return render_template('signup_tutor.html')

@app.route('/student-dashboard')
def student_dashboard():
    tutors = Tutor.query.all()
    return render_template('student_dashboard.html', tutors=tutors)

@app.route('/tutor-dashboard')
def tutor_dashboard():
    students = Student.query.all()
    return render_template('tutor_dashboard.html', students=students)

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Admin.query.filter_by(email=email, password=password).first()
        if admin:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    students = Student.query.all()
    tutors = Tutor.query.all()
    return render_template('admin_dashboard.html', students=students, tutors=tutors)

@app.route('/admin-logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/about')
def about():
    return render_template('about.html', title="About GuruGO", description="Learn more about GuruGO and our mission to connect students with the best tutors in Pune.", keywords="about GuruGO, home tutor platform Pune")

@app.route('/welcome')
def welcome():
    show_popup = session.pop('show_popup', False)
    student_name = session.pop('student_name', 'Student')
    return render_template('welcome.html', show_popup=show_popup, name=student_name)

@app.route('/welcome-tutor')
def welcome_tutor():
    show_popup = session.pop('show_popup', False)
    name = session.pop('tutor_name', 'Tutor')
    return render_template('welcome_tutor.html', show_popup=show_popup, name=name)

@app.route('/tutor-info')
def tutor_info():
    return render_template('tutor_info.html')

@app.route('/terms')
def terms():
    return render_template('terms.html', title="Terms & Conditions - GuruGO", description="Read the terms and conditions for using GuruGO's tutor finding services.", keywords="GuruGO terms, tutor terms Pune")

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html', title="Privacy Policy - GuruGO", description="GuruGO's privacy policy explains how we handle your data.", keywords="GuruGO privacy, data policy Pune")

# Blogs with SEO
@app.route('/blog/home-tuition-vs-group-coaching')
def blog_1():
    return render_template('blogs/home_tuition_vs_group_coaching.html', title="Home Tuition vs Group Coaching - Which is Better? | GuruGO", description="Learn the key differences between home tuition and group coaching to make the best choice for your learning needs.", keywords="home tuition vs group coaching, private tutor Pune, coaching classes Pune")

@app.route('/blog/how-to-choose-home-tutor')
def blog_2():
    return render_template('blogs/how_to_choose_home_tutor.html', title="How to Choose a Home Tutor in Pune | GuruGO", description="A complete guide on choosing the right home tutor in Pune for your needs.", keywords="choose home tutor Pune, private tuition guide")

@app.route('/blog/home-tuition-benefits-pune')
def blog_3():
    return render_template('blogs/home_tuition_benefits_pune.html', title="Benefits of Home Tuition in Pune | GuruGO", description="Discover the advantages of personalized home tuition in Pune.", keywords="home tuition benefits Pune, private tutor advantages")

@app.route('/blog/verified-home-tutors-gurugo')
def blog_4():
    return render_template('blogs/verified_home_tutors_gurugo.html', title="Verified Home Tutors with GuruGO | Pune", description="Find verified and trusted home tutors in Pune with GuruGO.", keywords="verified tutors Pune, trusted home tutor")

@app.route('/blog/online-vs-offline-tuition')
def blog_5():
    return render_template('blogs/online_vs_offline_tuition.html', title="Online vs Offline Tuition - Which is Right for You? | GuruGO", description="Compare the pros and cons of online and offline tuition.", keywords="online tuition Pune, offline tuition classes")

@app.route('/blog/subject-wise-tutor-guide')
def blog_6():
    return render_template('blogs/subject_wise_tutor_guide.html', title="Subject-Wise Tutor Guide for Pune Students | GuruGO", description="Find the right tutor for your subject and board in Pune.", keywords="subject wise tutor Pune, CBSE ICSE SSC tutors")

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return ext.sitemap()

@ext.register_generator
def index():
    yield 'home', {}
    yield 'signup_student', {}
    yield 'signup_tutor', {}
    yield 'student_dashboard', {}
    yield 'tutor_dashboard', {}
    yield 'admin_login', {}
    yield 'about', {}
    yield 'terms', {}
    yield 'privacy_policy', {}
    yield 'blog_1', {}
    yield 'blog_2', {}
    yield 'blog_3', {}
    yield 'blog_4', {}
    yield 'blog_5', {}
    yield 'blog_6', {}

# ========================
# App Runner
# ========================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(email="admin@example.com").first():
            admin = Admin(email="admin@example.com", password="admin123")
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin created.")
        else:
            print("ℹ️ Admin already exists.")

    app.run(host="0.0.0.0", port=5000, debug=False)
