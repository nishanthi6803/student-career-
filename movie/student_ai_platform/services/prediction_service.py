import pandas as pd
import numpy as np
import joblib
import os
import shap
import matplotlib.pyplot as plt
from io import BytesIO
import base64

class PredictionService:
    def __init__(self):
        self.model_path = os.path.join('models', 'career_model.pkl')
        self.salary_model_path = os.path.join('models', 'salary_model.pkl')
        self.model_data = None
        self.salary_data = None
        self._load_models()

    def _load_models(self):
        if os.path.exists(self.model_path):
            self.model_data = joblib.load(self.model_path)
        if os.path.exists(self.salary_model_path):
            self.salary_data = joblib.load(self.salary_model_path)

    def predict_career(self, features_dict):
        """
        features_dict: {cgpa, aptitude, coding, comm, leadership, interest}
        """
        if not self.model_data:
            return None, None

        model = self.model_data['model']
        scaler = self.model_data['scaler']
        le_interest = self.model_data['le_interest']
        le_career = self.model_data['le_career']

        # Encode interest
        interest_encoded = le_interest.transform([features_dict['interest']])[0]
        
        # Prepare feature array
        X = np.array([[
            features_dict['cgpa'],
            features_dict['aptitude'],
            features_dict['coding'],
            features_dict['comm'],
            features_dict['leadership'],
            interest_encoded
        ]])
        
        X_scaled = scaler.transform(X)
        
        # Prediction
        pred_idx = model.predict(X_scaled)[0]
        career = le_career.inverse_transform([pred_idx])[0]
        
        # Probabilities for confidence calibration
        probs = model.predict_proba(X_scaled)[0]
        confidence = round(np.max(probs) * 100, 2)
        
        return career, confidence

    def get_explanation(self, features_dict):
        """
        Generates SHAP values for explainability
        """
        if not self.model_data:
            return None

        model = self.model_data['model']
        scaler = self.model_data['scaler']
        le_interest = self.model_data['le_interest']
        
        interest_encoded = le_interest.transform([features_dict['interest']])[0]
        X = np.array([[
            features_dict['cgpa'],
            features_dict['aptitude'],
            features_dict['coding'],
            features_dict['comm'],
            features_dict['leadership'],
            interest_encoded
        ]])
        X_scaled = scaler.transform(X)
        
        # SHAP calculation (KernelExplainer for model-agnostic or TreeExplainer for RF/DT)
        # Using a subset of training data for background
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_scaled)
        
        # Generate plot
        plt.figure(figsize=(10, 6))
        # Plot for the predicted class
        pred_idx = model.predict(X_scaled)[0]
        shap.force_plot(explainer.expected_value[pred_idx], shap_values[pred_idx], X[0], 
                        feature_names=self.model_data['features'], matplotlib=True, show=False)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close()
        
        return image_base64

    def predict_salary(self, career, skill_score):
        """
        Predicts starting salary based on career and skills
        """
        # Base salaries per career (simplified regression logic)
        career_base = {
            'AI Engineer': 80000,
            'Data Scientist': 75000,
            'Web Developer': 60000,
            'Software Developer': 65000,
            'Cyber Security Analyst': 72000,
            'Business Analyst': 55000,
            'UI/UX Designer': 58000
        }
        
        base = career_base.get(career, 50000)
        # Multiplier based on skill score (1-10)
        multiplier = 1 + (skill_score - 5) * 0.1
        predicted = round(base * multiplier, 2)
        
        # 5-year projection
        projection = [round(predicted * (1.1 ** i), 2) for i in range(1, 6)]
        
        return predicted, projection
