from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models.database import db, User, StudentProfile, InterviewAttempt
import joblib
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.before_request
@login_required
def check_admin():
    if current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('student.dashboard'))

@admin_bp.route('/analytics')
def analytics():
    total_students = StudentProfile.query.count()
    users = User.query.all()
    profiles = StudentProfile.query.all()
    
    # Aggregates
    career_counts = {}
    total_intel = 0
    for p in profiles:
        career_counts[p.predicted_career] = career_counts.get(p.predicted_career, 0) + 1
        total_intel += (p.intelligence_score or 0)
        
    avg_intel = round(total_intel / total_students, 2) if total_students > 0 else 0
    top_career = max(career_counts, key=career_counts.get) if career_counts else "N/A"
    
    # Model info
    model_path = os.path.join('models', 'career_model.pkl')
    model_info = {}
    if os.path.exists(model_path):
        data = joblib.load(model_path)
        model_info = {'accuracy': f"{data['accuracy']*100:.2f}%"}
        
    return render_template('admin_analytics.html', 
                           total_students=total_students,
                           avg_intel=avg_intel,
                           top_career=top_career,
                           model_info=model_info,
                           career_counts=career_counts)

@admin_bp.route('/students')
def list_students():
    students = StudentProfile.query.all()
    return render_template('admin_students.html', students=students)
