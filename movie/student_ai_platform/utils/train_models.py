import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, mean_absolute_error
import joblib
import os

def generate_advanced_dataset(num_samples=2000):
    interests = ['AI/ML', 'Data Science', 'Web Development', 'UI/UX Design', 'Cyber Security', 'Business Analyst', 'Software Engineering']
    
    data = {
        'CGPA': np.round(np.random.uniform(2.5, 10.0, num_samples), 2),
        'AptitudeScore': np.random.randint(50, 100, num_samples),
        'CodingSkill': np.random.randint(1, 10, num_samples),
        'CommunicationSkill': np.random.randint(1, 10, num_samples),
        'LeadershipScore': np.random.randint(1, 10, num_samples),
        'InterestDomain': [np.random.choice(interests) for _ in range(num_samples)]
    }
    
    df = pd.DataFrame(data)
    
    def determine_career(row):
        if row['InterestDomain'] == 'AI/ML' and row['CodingSkill'] > 7: return 'AI Engineer'
        if row['InterestDomain'] == 'Data Science' and row['AptitudeScore'] > 80: return 'Data Scientist'
        if row['InterestDomain'] == 'Web Development' and row['CodingSkill'] > 6: return 'Web Developer'
        if row['InterestDomain'] == 'UI/UX Design' and row['CommunicationSkill'] > 7: return 'UI/UX Designer'
        if row['InterestDomain'] == 'Cyber Security' and row['CodingSkill'] > 7: return 'Cyber Security Analyst'
        if row['InterestDomain'] == 'Business Analyst' and row['CommunicationSkill'] > 7: return 'Business Analyst'
        return 'Software Developer' if row['CodingSkill'] > 5 else 'General IT'

    df['CareerPath'] = df.apply(determine_career, axis=1)
    
    # Salary logic based on career and skills
    base_salaries = {
        'AI Engineer': 85000, 'Data Scientist': 80000, 'Cyber Security Analyst': 78000,
        'Software Developer': 70000, 'Web Developer': 65000, 'UI/UX Designer': 62000,
        'Business Analyst': 60000, 'General IT': 50000
    }
    df['Salary'] = df.apply(lambda r: base_salaries[r['CareerPath']] * (1 + (r['CodingSkill']-5)*0.05 + (r['CGPA']-3)*0.1), axis=1)
    
    return df

def train_and_save():
    df = generate_advanced_dataset()
    os.makedirs('models', exist_ok=True)
    
    # 1. Career Model (Classifier)
    le_interest = LabelEncoder()
    df['InterestEncoded'] = le_interest.fit_transform(df['InterestDomain'])
    
    le_career = LabelEncoder()
    df['CareerEncoded'] = le_career.fit_transform(df['CareerPath'])
    
    features = ['CGPA', 'AptitudeScore', 'CodingSkill', 'CommunicationSkill', 'LeadershipScore', 'InterestEncoded']
    X = df[features]
    y = df['CareerEncoded']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    acc = accuracy_score(y_test, model.predict(X_test_scaled))
    print(f"Career Model Accuracy: {acc:.4f}")
    
    joblib.dump({
        'model': model, 'scaler': scaler, 
        'le_interest': le_interest, 'le_career': le_career,
        'features': features, 'accuracy': acc
    }, 'models/career_model.pkl')
    
    # 2. Salary Model (Regressor)
    # Binary encoding or similar for career in salary model
    X_sal = df[['CodingSkill', 'CGPA', 'CareerEncoded']]
    y_sal = df['Salary']
    
    sal_model = RandomForestRegressor(n_estimators=100, random_state=42)
    sal_model.fit(X_sal, y_sal)
    print(f"Salary Model Trained (MAE: {mean_absolute_error(y_sal, sal_model.predict(X_sal)):.2f})")
    joblib.dump(sal_model, 'models/salary_model.pkl')

if __name__ == "__main__":
    train_and_save()
