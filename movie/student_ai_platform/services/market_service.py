class MarketService:
    def __init__(self):
        # Market data (Simulated demand/growth)
        self.market_data = {
            'AI Engineer': {'demand': 95, 'growth': 35, 'trend': 'Rising'},
            'Data Scientist': {'demand': 90, 'growth': 25, 'trend': 'Stable'},
            'Web Developer': {'demand': 85, 'growth': 15, 'trend': 'High'},
            'Software Developer': {'demand': 88, 'growth': 20, 'trend': 'Very High'},
            'Cyber Security Analyst': {'demand': 92, 'growth': 40, 'trend': 'Critical'},
            'Business Analyst': {'demand': 75, 'growth': 10, 'trend': 'Stable'},
            'UI/UX Designer': {'demand': 80, 'growth': 18, 'trend': 'Rising'}
        }

    def get_market_insights(self, career):
        return self.market_data.get(career, {'demand': 50, 'growth': 5, 'trend': 'Variable'})

    def get_all_market_data(self):
        return self.market_data
