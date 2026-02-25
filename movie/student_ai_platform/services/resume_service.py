try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None
except Exception:
    nlp = None

import os
import io
import PyPDF2
import json

class ResumeService:
    def __init__(self):
        # Load spaCy NLP model
        self.nlp = nlp

    def extract_text_from_pdf(self, pdf_file):
        text = ""
        try:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text

    def analyze_resume(self, text, target_career):
        """
        Extracts skills and compares with target career requirements
        """
        # Dictionary of required skills for careers
        career_requirements = {
            'AI Engineer': ['python', 'pytorch', 'tensorflow', 'machine learning', 'deep learning', 'git', 'sql'],
            'Data Scientist': ['python', 'r', 'statistics', 'pandas', 'sql', 'scikit-learn', 'data visualization'],
            'Web Developer': ['html', 'css', 'javascript', 'react', 'node', 'django', 'flask', 'api'],
            'Software Developer': ['java', 'c++', 'python', 'algorithms', 'data structures', 'system design'],
            'Cyber Security Analyst': ['network security', 'linux', 'ethical hacking', 'firewalls', 'cryptography'],
            'Business Analyst': ['excel', 'tableau', 'power bi', 'sql', 'business logic', 'presentation'],
            'UI/UX Designer': ['figma', 'sketch', 'adobe xd', 'user research', 'wireframing', 'prototyping']
        }

        requirements = career_requirements.get(target_career, [])
        found_skills = []
        
        # Simple keyword matching using NLP tokens
        doc = self.nlp(text.lower()) if self.nlp else None
        text_content = text.lower()
        
        for skill in requirements:
            if skill in text_content:
                found_skills.append(skill)
        
        missing_skills = [s for s in requirements if s not in found_skills]
        
        match_score = round((len(found_skills) / len(requirements)) * 100, 2) if requirements else 0
        ats_score = round(match_score * 0.8 + 10, 2) # Adding base for formatting etc.

        return {
            'found_skills': found_skills,
            'missing_skills': missing_skills,
            'match_score': match_score,
            'ats_score': ats_score
        }
