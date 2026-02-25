from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import joblib
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-career-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default='student') # student, admin

class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    aptitude_score = db.Column(db.Integer)
    coding_skill = db.Column(db.Integer)
    communication_skill = db.Column(db.Integer)
    leadership_score = db.Column(db.Integer)
    interest_area = db.Column(db.String(100))
    predicted_career = db.Column(db.String(100))
    intelligence_score = db.Column(db.Float)
    career_readiness_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Scoring Logic
def calculate_scores(profile):
    # Intelligence Score: Weighted average of performance metrics
    intel_score = (profile.cgpa * 20) * 0.4 + \
                  (profile.aptitude_score) * 0.3 + \
                  (profile.coding_skill * 10) * 0.3
    
    # Career Readiness: Average of skills and cgpa
    readiness = (profile.coding_skill * 10 + profile.communication_skill * 10 + profile.leadership_score * 10 + profile.cgpa * 25) / 4
    
    return round(intel_score, 2), round(readiness, 2)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
            
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('dashboard.html', profile=profile)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        # Load model data
        model_path = os.path.join('model', 'career_model.pkl')
        if not os.path.exists(model_path):
            # Try without model prefix if in model subdir context
            model_path = 'career_model.pkl'
            
        model_data = joblib.load(model_path)
        model = model_data['model']
        scaler = model_data['scaler']
        le_interest = model_data['le_interest']
        le_career = model_data['le_career']
        
        # Get form data
        name = request.form.get('name')
        cgpa = float(request.form.get('cgpa'))
        aptitude = int(request.form.get('aptitude'))
        coding = int(request.form.get('coding'))
        comm = int(request.form.get('communication'))
        leadership = int(request.form.get('leadership'))
        interest = request.form.get('interest')
        
        # Preprocess input
        interest_encoded = le_interest.transform([interest])[0]
        input_features = np.array([[cgpa, aptitude, coding, comm, leadership, interest_encoded]])
        input_scaled = scaler.transform(input_features)
        
        # Predict
        prediction_idx = model.predict(input_scaled)[0]
        career_name = le_career.inverse_transform([prediction_idx])[0]
        
        # Save or update profile
        profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
        if not profile:
            profile = StudentProfile(user_id=current_user.id)
            db.session.add(profile)
            
        profile.name = name
        profile.cgpa = cgpa
        profile.aptitude_score = aptitude
        profile.coding_skill = coding
        profile.communication_skill = comm
        profile.leadership_score = leadership
        profile.interest_area = interest
        profile.predicted_career = career_name
        
        profile.intelligence_score, profile.career_readiness_score = calculate_scores(profile)
        db.session.commit()
        
        return redirect(url_for('result'))
    except Exception as e:
        flash(f'Error during prediction: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/result')
@login_required
def result():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for('dashboard'))
        
    # Mock some roadmap data based on career
    roadmaps = {
        'AI Engineer': ['Master Python & PyTorch', 'Learn Deep Learning', 'Build Kaggle Notebooks'],
        'Data Scientist': ['Learn SQL & R/Python', 'Statistics & Probability', 'Data Visualization Tools'],
        'Web Developer': ['Master JavaScript & React', 'Learn Backend (Node/Django)', 'Project Deployment'],
        'Software Developer': ['Data Structures & Algorithms', 'System Design Base', 'Master one compiled language'],
        'Cyber Security Analyst': ['Network Protocols', 'Ethical Hacking Certs', 'Security Audits'],
        'Business Analyst': ['Excel Mastery', 'Tableau/PowerBI', 'Domain Knowledge'],
        'UI/UX Designer': ['Figma/Adobe XD', 'Design Systems', 'User Research']
    }
    
    roadmap = roadmaps.get(profile.predicted_career, ['General Skill Development'])
    
    return render_template('result.html', profile=profile, roadmap=roadmap)

@app.route('/export_pdf')
@login_required
def export_pdf():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for('dashboard'))
        
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    p.setFont("Helvetica-Bold", 24)
    p.drawString(100, 750, "StudentAI Career Report")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 720, f"Name: {profile.name}")
    p.drawString(100, 705, f"Email: {current_user.email}")
    p.drawString(100, 690, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
    
    p.line(100, 680, 500, 680)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 650, "Prediction Result")
    p.setFont("Helvetica", 14)
    p.drawString(100, 630, f"Predicted Career: {profile.predicted_career}")
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 590, "Scores")
    p.setFont("Helvetica", 12)
    p.drawString(100, 570, f"Intelligence Score: {profile.intelligence_score}/100")
    p.drawString(100, 555, f"Career Readiness: {profile.career_readiness_score}%")
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 520, "Skill Analysis")
    p.setFont("Helvetica", 12)
    p.drawString(100, 500, f"CGPA: {profile.cgpa}/4.0")
    p.drawString(100, 485, f"Coding Skill: {profile.coding_skill}/10")
    p.drawString(100, 470, f"Communication: {profile.communication_skill}/10")
    p.drawString(100, 455, f"Leadership: {profile.leadership_score}/10")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{profile.name}_Career_Report.pdf", mimetype='application/pdf')

# Admin panel dummy
@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    # Load model info
    model_path = os.path.join('model', 'career_model.pkl')
    model_info = {}
    if os.path.exists(model_path):
        model_data = joblib.load(model_path)
        model_info = {
            'accuracy': f"{model_data['accuracy'] * 100:.2f}%",
            'features': ", ".join(model_data['features'])
        }
        
    return render_template('admin.html', model_info=model_info)

# Initialize DB
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create a default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@studentai.com', password='adminpassword', role='admin')
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
