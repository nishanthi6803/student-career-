from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.database import db, StudentProfile, ResumeData, InterviewAttempt
from services.prediction_service import PredictionService
from services.resume_service import ResumeService
from services.personality_service import PersonalityService
from services.interview_service import InterviewService
from services.market_service import MarketService
import json

student_bp = Blueprint('student', __name__)

# Initialize Services
prediction_service = PredictionService()
resume_service = ResumeService()
personality_service = PersonalityService()
interview_service = InterviewService()
market_service = MarketService()

@student_bp.route('/dashboard')
@login_required
def dashboard():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    market_data = market_service.get_all_market_data()
    return render_template('dashboard.html', profile=profile, market_data=market_data)

@student_bp.route('/predict', methods=['POST'])
@login_required
def predict():
    data = {
        'cgpa': float(request.form.get('cgpa')),
        'aptitude': int(request.form.get('aptitude')),
        'coding': int(request.form.get('coding')),
        'comm': int(request.form.get('communication')),
        'leadership': int(request.form.get('leadership')),
        'interest': request.form.get('interest')
    }
    
    career, confidence = prediction_service.predict_career(data)
    
    # Calculate Intelligence & Readiness (Re-using logic from monolithic)
    intel_score = round((data['cgpa'] * 20) * 0.4 + (data['aptitude']) * 0.3 + (data['coding'] * 10) * 0.3, 2)
    readiness = round((data['coding'] * 10 + data['comm'] * 10 + data['leadership'] * 10 + data['cgpa'] * 25) / 4, 2)
    
    # Salary prediction
    salary, projection = prediction_service.predict_salary(career, data['coding'])
    
    # Update Profile
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = StudentProfile(user_id=current_user.id)
        db.session.add(profile)
        
    profile.name = request.form.get('name')
    profile.cgpa = data['cgpa']
    profile.aptitude_score = data['aptitude']
    profile.coding_skill = data['coding']
    profile.communication_skill = data['comm']
    profile.leadership_score = data['leadership']
    profile.interest_area = data['interest']
    profile.predicted_career = career
    profile.predicted_salary = salary
    profile.intelligence_score = intel_score
    profile.career_readiness_score = readiness
    
    db.session.commit()
    return redirect(url_for('student.result'))

@student_bp.route('/result')
@login_required
def result():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for('student.dashboard'))
        
    # Get explanation (SHAP)
    # Note: SHAP image generation might be slow, could be async in prod
    features = {
        'cgpa': profile.cgpa, 'aptitude': profile.aptitude_score, 
        'coding': profile.coding_skill, 'comm': profile.communication_skill,
        'leadership': profile.leadership_score, 'interest': profile.interest_area
    }
    explanation_img = prediction_service.get_explanation(features)
    
    # Get Market Insights
    market_info = market_service.get_market_insights(profile.predicted_career)
    
    return render_template('result.html', profile=profile, explanation=explanation_img, market=market_info)

@student_bp.route('/resume-analysis', methods=['GET', 'POST'])
@login_required
def resume_analysis():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    analysis_result = None
    
    if request.method == 'POST':
        file = request.files.get('resume')
        if file and file.filename.endswith('.pdf'):
            text = resume_service.extract_text_from_pdf(file)
            analysis_result = resume_service.analyze_resume(text, profile.predicted_career)
            
            # Save or Update Resume Data
            res_data = ResumeData.query.filter_by(student_id=profile.id).first()
            if not res_data:
                res_data = ResumeData(student_id=profile.id)
                db.session.add(res_data)
            
            res_data.filename = file.filename
            res_data.extracted_skills = json.dumps(analysis_result['found_skills'])
            res_data.missing_skills = json.dumps(analysis_result['missing_skills'])
            profile.ats_score = analysis_result['ats_score']
            db.session.commit()
            
    return render_template('resume_analysis.html', profile=profile, result=analysis_result)

@student_bp.route('/personality', methods=['GET', 'POST'])
@login_required
def personality():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    result = None
    if request.method == 'POST':
        text = request.form.get('description')
        result = personality_service.analyze_personality(text)
        profile.personality_type = result['dominant_trait']
        db.session.commit()
        
    return render_template('personality.html', profile=profile, result=result)

@student_bp.route('/interview', methods=['GET', 'POST'])
@login_required
def interview():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile or not profile.predicted_career:
        flash('Please complete your profile prediction first.', 'warning')
        return redirect(url_for('student.dashboard'))
        
    question = None
    evaluation = None
    
    if request.method == 'POST':
        if 'start' in request.form:
            question = interview_service.generate_question(profile.predicted_career)
        elif 'submit_answer' in request.form:
            q = request.form.get('question')
            a = request.form.get('answer')
            evaluation = interview_service.evaluate_answer(q, a)
            
            # Save attempt
            attempt = InterviewAttempt(
                student_id=profile.id,
                career_context=profile.predicted_career,
                question=q,
                answer=a,
                feedback=evaluation['feedback'],
                score=evaluation['score']
            )
            db.session.add(attempt)
            db.session.commit()
            
    return render_template('interview.html', profile=profile, question=question, evaluation=evaluation)
