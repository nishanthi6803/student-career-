from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, admin, counselor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    predicted_salary = db.Column(db.Float)
    intelligence_score = db.Column(db.Float)
    career_readiness_score = db.Column(db.Float)
    ats_score = db.Column(db.Float)
    personality_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ResumeData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    filename = db.Column(db.String(255))
    extracted_skills = db.Column(db.Text)  # JSON string
    missing_skills = db.Column(db.Text)    # JSON string
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)

class InterviewAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profile.id'), nullable=False)
    career_context = db.Column(db.String(100))
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    feedback = db.Column(db.Text)
    score = db.Column(db.Float)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
