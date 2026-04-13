import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve
)

def get_metrics_report(y_true, y_pred, y_prob=None):
    """Calculates common classification metrics."""
    metrics = {
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred, pos_label=1),
        "Recall": recall_score(y_true, y_pred, pos_label=1),
        "F1 Score": f1_score(y_true, y_pred, pos_label=1),
    }

    if y_prob is not None:
        metrics["ROC-AUC"] = roc_auc_score(y_true, y_prob)

    return metrics

def format_metrics_report(metrics, model_name="Baseline Model"):
    """Formats metrics dictionary into a readable string."""
    report = f"--- {model_name} Evaluation ---\n"
    for k, v in metrics.items():
        report += f"{k}: {v:.4f}\n"
    return report

def save_confusion_matrix(y_true, y_pred, output_path):
    """Plots and saves the confusion matrix."""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['No Churn', 'Churn'], 
                yticklabels=['No Churn', 'Churn'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig(output_path)
    plt.close()

def save_classification_report(y_true, y_pred, output_path):
    """Saves the detailed classification report to a text file."""
    report = classification_report(y_true, y_pred, target_names=['No Churn', 'Churn'])
    with open(output_path, 'w') as f:
        f.write(report)
    return report

def save_roc_curve(y_true, y_prob, output_path):
    """Plots and saves the ROC curve."""
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'ROC-AUC: {roc_auc_score(y_true, y_prob):.4f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve')
    plt.legend()
    plt.savefig(output_path)
    plt.close()
