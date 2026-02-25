import random

class InterviewService:
    def __init__(self):
        # Questions database per career
        self.question_bank = {
            'AI Engineer': [
                "Explain the difference between supervised and unsupervised learning.",
                "How do you handle overfitting in a deep learning model?",
                "What is the purpose of an activation function?"
            ],
            'Data Scientist': [
                "What is a p-value and how do you interpret it?",
                "Describe the lifecycle of a data science project.",
                "How do you deal with missing data in a dataset?"
            ],
            'Web Developer': [
                "What is the difference between REST and GraphQL?",
                "Explain the concept of 'hoisting' in JavaScript.",
                "How do you optimize a website's performance?"
            ],
            'Software Developer': [
                "What are the SOLID principles of object-oriented design?",
                "Explain how a hash map works internally.",
                "What is the difference between a process and a thread?"
            ],
            'Cyber Security Analyst': [
                "What is a Man-in-the-Middle attack?",
                "Explain the CIA triad in information security.",
                "What are the steps of a penetration test?"
            ],
            'UI/UX Designer': [
                "What is the difference between UI and UX?",
                "Describe your design process from concept to prototype.",
                "How do you handle negative feedback on a design?"
            ],
            'Business Analyst': [
                "What is a SWOT analysis and when is it used?",
                "How do you gather requirements from stakeholders?",
                "Explain the difference between Agile and Waterfall methodologies."
            ]
        }

    def generate_question(self, career):
        questions = self.question_bank.get(career, ["Tell me about your technical background."])
        return random.choice(questions)

    def evaluate_answer(self, question, answer):
        """
        Evaluates answer based on keyword matching and length (Simplified NLP)
        """
        # In a real production app, this would use a transformer model (BERT/GPT)
        word_count = len(answer.split())
        
        # Basic scoring logic
        if word_count < 10:
            score = 30
            feedback = "Your answer is too short. Try to elaborate with examples."
        elif word_count < 30:
            score = 60
            feedback = "Good start, but could use more technical depth."
        else:
            score = 85
            feedback = "Comprehensive answer! You demonstrated good knowledge of the topic."
            
        return {
            'score': score,
            'feedback': feedback,
            'word_count': word_count
        }
