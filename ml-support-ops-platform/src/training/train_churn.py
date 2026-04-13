import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt

from src.ingestion.load_churn_data import load_churn_data
from src.features.preprocess import build_preprocessing_pipeline, clean_churn_data, get_feature_names
from src.evaluation.evaluate import (
    get_metrics_report, format_metrics_report, 
    save_confusion_matrix, save_classification_report, save_roc_curve
)
from src.config import TARGET_COL, ID_COL
from src.utils.paths import MODELS_PATH, REPORTS_PATH

def train_and_evaluate(X_train, X_test, y_train, y_test, model, model_name):
    """Generic training and evaluation function for different models."""
    
    preprocessor = build_preprocessing_pipeline()
    clf_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', model)
    ])
    
    print(f"Training {model_name}...")
    clf_pipeline.fit(X_train, y_train)
    
    # 7. Evaluate
    y_pred = clf_pipeline.predict(X_test)
    y_prob = clf_pipeline.predict_proba(X_test)[:, 1]
    
    metrics = get_metrics_report(y_test, y_pred, y_prob)
    report = format_metrics_report(metrics, model_name=model_name)
    print(report)
    
    # Save artifacts
    MODELS_PATH.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf_pipeline, MODELS_PATH / f"churn_{model_name.lower().replace(' ', '_')}.joblib")
    
    REPORTS_PATH.mkdir(parents=True, exist_ok=True)
    report_base = REPORTS_PATH / f"churn_{model_name.lower().replace(' ', '_')}"
    
    with open(f"{report_base}_metrics.txt", "w") as f:
        f.write(report)
    
    save_confusion_matrix(y_test, y_pred, f"{report_base}_cm.png")
    save_classification_report(y_test, y_pred, f"{report_base}_report.txt")
    save_roc_curve(y_test, y_prob, f"{report_base}_roc.png")
    
    # Feature Importance
    extract_feature_importance(clf_pipeline, model_name, report_base)
    
    return metrics

def extract_feature_importance(clf_pipeline, model_name, report_base):
    """Extracts and plots feature importance if available."""
    preprocessor = clf_pipeline.named_steps['preprocessor']
    model = clf_pipeline.named_steps['classifier']
    
    feature_names = get_feature_names(preprocessor)
    
    importances = None
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_[0])
        
    if importances is not None:
        feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)
        plt.figure(figsize=(10, 12))
        feat_imp.head(20).plot(kind='barh')
        plt.title(f'Top 20 Feature Importances - {model_name}')
        plt.tight_layout()
        plt.savefig(f"{report_base}_feature_importance.png")
        plt.close()
        print(f"Feature importance saved to {report_base}_feature_importance.png")

def main():
    # 1. Load data
    df = load_churn_data()
    
    # 2. Clean data
    df = clean_churn_data(df)
    
    # 3. Prepare Features & Target
    y = df[TARGET_COL].apply(lambda x: 1 if x == 'Yes' else 0)
    X = df.drop(columns=[TARGET_COL, ID_COL])
    
    # 4. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Model 1: Logistic Regression
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    train_and_evaluate(X_train, X_test, y_train, y_test, lr_model, "Logistic Regression")
    
    # Model 2: Random Forest
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    train_and_evaluate(X_train, X_test, y_train, y_test, rf_model, "Random Forest")

if __name__ == "__main__":
    main()
