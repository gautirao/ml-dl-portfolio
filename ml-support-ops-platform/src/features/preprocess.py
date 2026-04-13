import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from src.config import NUMERICAL_FEATURES, CATEGORICAL_FEATURES

def build_preprocessing_pipeline():
    """Returns a scikit-learn preprocessing pipeline."""
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, NUMERICAL_FEATURES),
            ('cat', categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )

    return preprocessor

def clean_churn_data(df):
    """
    Handles specific cleaning steps like converting TotalCharges to numeric.
    Does not include scaling or imputation - those are in the pipeline.
    """
    df = df.copy()
    # TotalCharges is often an object with whitespace in this dataset
    df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
    return df

def get_feature_names(column_transformer):
    """
    Extracts feature names from a fitted scikit-learn ColumnTransformer.
    Works for OneHotEncoder, StandardScaler, etc.
    """
    feature_names = []
    
    for name, transformer, columns in column_transformer.transformers_:
        if name == 'remainder' and transformer == 'drop':
            continue
        
        # If the transformer is a pipeline, we need to handle its steps
        if isinstance(transformer, Pipeline):
            # Extract names from the last step or use get_feature_names_out if available
            if hasattr(transformer, 'get_feature_names_out'):
                names = transformer.get_feature_names_out(columns)
                feature_names.extend(names)
            else:
                # Manual fallback if needed, but get_feature_names_out is standard now
                feature_names.extend(columns)
        elif hasattr(transformer, 'get_feature_names_out'):
            names = transformer.get_feature_names_out(columns)
            feature_names.extend(names)
        else:
            feature_names.extend(columns)
            
    return feature_names
