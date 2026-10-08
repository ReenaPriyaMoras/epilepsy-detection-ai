import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import confusion_matrix, roc_curve, auc, precision_recall_curve

def plot_confusion_matrix(y_true, y_pred, save_dir):
    """Generates and saves the confusion matrix."""
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Normal", "Epileptic"], yticklabels=["Normal", "Epileptic"])
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "confusion_matrix.png"), dpi=300)
    plt.close()

def plot_roc_curve(y_true, y_prob, save_dir):
    """Generates and saves the ROC curve."""
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(6,5))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "roc_curve.png"), dpi=300)
    plt.close()

def plot_pr_curve(y_true, y_prob, save_dir):
    """Generates and saves the Precision-Recall curve."""
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    
    plt.figure(figsize=(6,5))
    plt.plot(recall, precision, color='purple', lw=2, label='PR Curve')
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve')
    plt.legend(loc="lower left")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "pr_curve.png"), dpi=300)
    plt.close()

def plot_confidence_distribution(y_true, y_prob, save_dir):
    """Generates and saves the prediction confidence distribution."""
    # Convert true labels to array
    y_true = np.array(y_true)
    y_prob = np.array(y_prob)
    
    # Calculate confidence: distance from 0.5 threshold mapped to 0-1 (e.g. prob=0.9 -> conf=0.9 for class 1)
    # Actually confidence for class 1 is y_prob, confidence for class 0 is 1-y_prob
    # We can plot raw probability of being class 1.
    
    plt.figure(figsize=(7,5))
    sns.histplot(y_prob[y_true == 1], color="red", label="True: Epileptic", kde=True, stat="density", bins=20, alpha=0.5)
    sns.histplot(y_prob[y_true == 0], color="blue", label="True: Normal", kde=True, stat="density", bins=20, alpha=0.5)
    plt.axvline(x=0.5, color='black', linestyle='--', label="Threshold (0.5)")
    plt.title("Prediction Probability Distribution")
    plt.xlabel("Probability of Epileptic")
    plt.ylabel("Density")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "confidence_distribution.png"), dpi=300)
    plt.close()

def plot_explainability_summary(global_channel_imp, global_feature_imp, save_dir):
    """Plots and saves feature and channel importances."""
    # Channel importance
    channels, c_scores = zip(*global_channel_imp.items())
    # sort
    c_indices = np.argsort(c_scores)[::-1][:15] # Top 15
    top_channels = [channels[i] for i in c_indices]
    top_c_scores = [c_scores[i] for i in c_indices]
    
    plt.figure(figsize=(8,5))
    sns.barplot(x=top_c_scores, y=top_channels, palette="viridis")
    plt.title("Top 15 Most Important EEG Channels")
    plt.xlabel("Average Importance Score")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "channel_importance.png"), dpi=300)
    plt.close()
    
    # Feature importance
    features, f_scores = zip(*global_feature_imp.items())
    f_indices = np.argsort(f_scores)[::-1][:10] # Top 10
    top_features = [features[i] for i in f_indices]
    top_f_scores = [f_scores[i] for i in f_indices]
    
    plt.figure(figsize=(8,5))
    sns.barplot(x=top_f_scores, y=top_features, palette="magma")
    plt.title("Top 10 Most Important Extracted Features")
    plt.xlabel("Average Importance Score")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, "feature_importance.png"), dpi=300)
    plt.close()
