import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score
import joblib
import os

# Set seed for reproducibility
np.random.seed(42)

def generate_synthetic_data(num_samples=1500):
    interests = ['Data Science', 'Web Development', 'AI/ML', 'Cyber Security', 'Business Analyst', 'UI/UX Design', 'Software Engineering']
    career_paths = {
        'Data Science': 'Data Scientist',
        'Web Development': 'Web Developer',
        'AI/ML': 'AI Engineer',
        'Cyber Security': 'Cyber Security Analyst',
        'Business Analyst': 'Business Analyst',
        'UI/UX Design': 'UI/UX Designer',
        'Software Engineering': 'Software Developer'
    }

    data = {
        'CGPA': np.round(np.random.uniform(2.5, 4.0, num_samples), 2),
        'AptitudeScore': np.random.randint(50, 100, num_samples),
        'CodingSkill': np.random.randint(1, 10, num_samples),
        'CommunicationSkill': np.random.randint(1, 10, num_samples),
        'LeadershipScore': np.random.randint(1, 10, num_samples),
        'InterestDomain': [np.random.choice(interests) for _ in range(num_samples)]
    }

    df = pd.DataFrame(data)

    def determine_career(row):
        # Add some logic-based fuzziness to make the model learn patterns
        if row['InterestDomain'] == 'AI/ML' and row['CodingSkill'] > 7:
            return 'AI Engineer'
        elif row['InterestDomain'] == 'Data Science' and row['AptitudeScore'] > 80:
            return 'Data Scientist'
        elif row['InterestDomain'] == 'Web Development' and row['CodingSkill'] > 6:
            return 'Web Developer'
        elif row['InterestDomain'] == 'UI/UX Design' and row['CommunicationSkill'] > 7:
            return 'UI/UX Designer'
        elif row['InterestDomain'] == 'Cyber Security' and row['CodingSkill'] > 7:
            return 'Cyber Security Analyst'
        elif row['InterestDomain'] == 'Business Analyst' and row['CommunicationSkill'] > 7:
            return 'Business Analyst'
        else:
            return career_paths[row['InterestDomain']]

    df['CareerPath'] = df.apply(determine_career, axis=1)
    return df

def train_and_save_model():
    print("Generating synthetic dataset...")
    df = generate_synthetic_data()
    
    # Save dataset for reference
    df.to_csv('student_career_dataset.csv', index=False)
    
    # Preprocessing
    le_interest = LabelEncoder()
    df['InterestDomain'] = le_interest.fit_transform(df['InterestDomain'])
    
    le_career = LabelEncoder()
    df['CareerPath'] = le_career.fit_transform(df['CareerPath'])
    
    X = df.drop('CareerPath', axis=1)
    y = df['CareerPath']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'Logistic Regression': LogisticRegression(),
        'Random Forest': RandomForestClassifier(n_estimators=100),
        'Decision Tree': DecisionTreeClassifier(),
        'KNN': KNeighborsClassifier()
    }
    
    best_model = None
    best_accuracy = 0
    best_model_name = ""
    
    print("\nTraining models and comparing accuracy:")
    for name, model in models.items():
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        acc = accuracy_score(y_test, y_pred)
        print(f"{name} Accuracy: {acc:.4f}")
        
        if acc > best_accuracy:
            best_accuracy = acc
            best_model = model
            best_model_name = name
            
    print(f"\nBest Model: {best_model_name} with Accuracy: {best_accuracy:.4f}")
    
    # Save the best model, scaler, and label encoders
    model_data = {
        'model': best_model,
        'scaler': scaler,
        'le_interest': le_interest,
        'le_career': le_career,
        'accuracy': best_accuracy,
        'features': X.columns.tolist()
    }
    
    joblib.dump(model_data, 'career_model.pkl')
    print("Model and preprocessing objects saved to career_model.pkl")

if __name__ == "__main__":
    train_and_save_model()
