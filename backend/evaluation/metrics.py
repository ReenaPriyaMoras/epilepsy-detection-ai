import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, balanced_accuracy_score, matthews_corrcoef,
    cohen_kappa_score, log_loss, confusion_matrix, classification_report
)

def compute_all_metrics(y_true, y_prob, y_pred):
    """
    Computes a comprehensive suite of classification metrics.
    y_true: list of true labels (0=Normal, 1=Epileptic)
    y_prob: list of predicted probabilities for class 1
    y_pred: list of predicted discrete labels
    """
    metrics = {}
    metrics["Accuracy"] = accuracy_score(y_true, y_pred)
    metrics["Precision"] = precision_score(y_true, y_pred, zero_division=0)
    metrics["Recall"] = recall_score(y_true, y_pred, zero_division=0)
    
    # Specificity = TN / (TN + FP)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    metrics["Specificity"] = specificity
    
    metrics["F1-score"] = f1_score(y_true, y_pred, zero_division=0)
    
    try:
        metrics["ROC-AUC"] = roc_auc_score(y_true, y_prob)
    except ValueError:
        metrics["ROC-AUC"] = 0.0 # fallback if only one class in y_true
        
    metrics["Balanced Accuracy"] = balanced_accuracy_score(y_true, y_pred)
    metrics["MCC"] = matthews_corrcoef(y_true, y_pred)
    metrics["Cohen's Kappa"] = cohen_kappa_score(y_true, y_pred)
    
    try:
        metrics["Log Loss"] = log_loss(y_true, y_prob)
    except ValueError:
        metrics["Log Loss"] = 0.0
        
    from sklearn.metrics import auc, precision_recall_curve
    try:
        precision_arr, recall_arr, _ = precision_recall_curve(y_true, y_prob)
        metrics["PR AUC"] = auc(recall_arr, precision_arr)
    except ValueError:
        metrics["PR AUC"] = 0.0
        
    metrics["TP"] = int(tp)
    metrics["TN"] = int(tn)
    metrics["FP"] = int(fp)
    metrics["FN"] = int(fn)
    
    return metrics

def get_classification_report(y_true, y_pred):
    """Returns the text-based classification report."""
    return classification_report(y_true, y_pred, target_names=["Normal", "Epileptic"], zero_division=0)
