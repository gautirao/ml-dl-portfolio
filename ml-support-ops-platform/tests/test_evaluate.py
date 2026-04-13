import numpy as np
from src.evaluation.evaluate import get_metrics_report

def test_get_metrics_report():
    y_true = [0, 1, 0, 1]
    y_pred = [0, 1, 1, 1]
    y_prob = [0.1, 0.9, 0.8, 0.7]
    
    metrics = get_metrics_report(y_true, y_pred, y_prob)
    
    assert "Accuracy" in metrics
    assert "Precision" in metrics
    assert "Recall" in metrics
    assert "F1 Score" in metrics
    assert "ROC-AUC" in metrics
    
    assert metrics["Accuracy"] == 0.75
    assert metrics["Recall"] == 1.0
