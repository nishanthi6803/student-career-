from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

class PersonalityService:
    def __init__(self):
        try:
            nltk.data.find('vader_lexicon')
        except LookupError:
            nltk.download('vader_lexicon')
        self.sia = SentimentIntensityAnalyzer()

    def analyze_personality(self, text):
        """
        Analyzes personality based on text input (self-description)
        """
        scores = self.sia.polarity_scores(text)
        
        # Mapping sentiment scores to pseudo-personality traits
        # This is a simplified NLP-based approximation
        traits = {
            'Openness': round((scores['pos'] * 0.6 + scores['neu'] * 0.4) * 10, 2),
            'Conscientiousness': round((scores['neu'] * 0.7 + scores['pos'] * 0.3) * 10, 2),
            'Extraversion': round((scores['pos'] * 0.8 + scores['compound'] * 0.2) * 10, 2),
            'Agreeableness': round((scores['pos'] * 0.9) * 10, 2),
            'Emotional Stability': round((1 - abs(scores['compound'] - 0.5)) * 10, 2)
        }
        
        # Dominant trait
        dominant = max(traits, key=traits.get)
        
        return {
            'traits': traits,
            'dominant_trait': dominant,
            'sentiment_scores': scores
        }
