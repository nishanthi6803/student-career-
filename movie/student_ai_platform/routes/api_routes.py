from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.database import StudentProfile
from services.prediction_service import PredictionService

api_bp = Blueprint('api', __name__)
prediction_service = PredictionService()

@api_bp.route('/predict', methods=['POST'])
# @jwt_required()  # Optional: enable for production security
def external_predict():
    data = request.json
    if not data:
        return jsonify({"error": "No input data provided"}), 400
        
    required = ['cgpa', 'aptitude', 'coding', 'comm', 'leadership', 'interest']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
        
    career, confidence = prediction_service.predict_career(data)
    salary, _ = prediction_service.predict_salary(career, data['coding'])
    
    return jsonify({
        "predicted_career": career,
        "confidence_score": confidence,
        "estimated_salary": salary,
        "status": "success"
    })
