import pandas as pd
import numpy as np
from src.features.preprocess import clean_churn_data, build_preprocessing_pipeline, get_feature_names

def test_clean_churn_data():
    df = pd.DataFrame({
        'TotalCharges': ['10.5', ' ', '20.0'],
        'Other': [1, 2, 3]
    })
    cleaned_df = clean_churn_data(df)
    assert pd.api.types.is_numeric_dtype(cleaned_df['TotalCharges'])
    assert np.isnan(cleaned_df['TotalCharges'][1])

def test_get_feature_names():
    df = pd.DataFrame({
        'tenure': [1, 2],
        'MonthlyCharges': [10.0, 20.0],
        'TotalCharges': [10.0, 20.0],
        'gender': ['Male', 'Female'],
        'SeniorCitizen': [0, 1],
        'Partner': ['Yes', 'No'],
        'Dependents': ['No', 'Yes'],
        'PhoneService': ['No', 'Yes'],
        'MultipleLines': ['No', 'Yes'],
        'InternetService': ['DSL', 'Fiber optic'],
        'OnlineSecurity': ['No', 'Yes'],
        'OnlineBackup': ['No', 'Yes'],
        'DeviceProtection': ['No', 'Yes'],
        'TechSupport': ['No', 'Yes'],
        'StreamingTV': ['No', 'Yes'],
        'StreamingMovies': ['No', 'Yes'],
        'Contract': ['Month-to-month', 'One year'],
        'PaperlessBilling': ['No', 'Yes'],
        'PaymentMethod': ['Electronic check', 'Mailed check']
    })
    
    pipeline = build_preprocessing_pipeline()
    pipeline.fit(df)
    
    feature_names = get_feature_names(pipeline)
    assert len(feature_names) > 0
    assert 'tenure' in feature_names
    assert any('gender' in name for name in feature_names)
