import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import (
    mean_absolute_error, 
    mean_squared_error, 
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    roc_curve
)

def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray, model_name: str, reports_dir: str = "reports") -> dict:
    """
    Computes MAE, RMSE, and R2 score for regression,
    saves the metrics as a JSON file, and generates evaluation plots.
    """
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    metrics = {
        "Model_Name": model_name,
        "MAE": round(float(mae), 4),
        "RMSE": round(float(rmse), 4),
        "R2_Score": round(float(r2), 4)
    }
    
    print(f"\n--- Regression Evaluation: {model_name} ---")
    print(f"MAE: {mae:.2f} minutes")
    print(f"RMSE: {rmse:.2f} minutes")
    print(f"R2 Score: {r2:.4f}")
    
    # Save metrics JSON
    metrics_path = os.path.join(reports_dir, "model_metrics", f"{model_name.lower().replace(' ', '_')}_regression_metrics.json")
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
        
    # Generate Plots
    graphs_dir = os.path.join(reports_dir, "graphs")
    os.makedirs(graphs_dir, exist_ok=True)
    
    # 1. Predicted vs Actual Plot
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x=y_true, y=y_pred, alpha=0.5, color="#4facfe")
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], "r--", lw=2)
    plt.title(f"Predicted vs Actual Delivery Time ({model_name})")
    plt.xlabel("Actual Delivery Time (Min)")
    plt.ylabel("Predicted Delivery Time (Min)")
    plt.tight_layout()
    plt.savefig(os.path.join(graphs_dir, f"{model_name.lower().replace(' ', '_')}_pred_vs_actual.png"))
    plt.close()
    
    # 2. Residuals Plot
    residuals = y_true - y_pred
    plt.figure(figsize=(8, 6))
    sns.histplot(residuals, kde=True, color="#00f2fe", bins=30)
    plt.axvline(0, color="red", linestyle="--")
    plt.title(f"Residuals Distribution ({model_name})")
    plt.xlabel("Residual Error (Actual - Predicted)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(graphs_dir, f"{model_name.lower().replace(' ', '_')}_residuals.png"))
    plt.close()
    
    return metrics

def evaluate_classification(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray, model_name: str, reports_dir: str = "reports") -> dict:
    """
    Computes accuracy, precision, recall, F1, and ROC AUC for classification,
    saves the metrics as a JSON file, and generates confusion matrix and ROC curves.
    """
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    
    try:
        auc = roc_auc_score(y_true, y_prob)
    except Exception:
        auc = 0.5  # In case target has only one class in batch
        
    metrics = {
        "Model_Name": model_name,
        "Accuracy": round(float(acc), 4),
        "Precision": round(float(prec), 4),
        "Recall": round(float(rec), 4),
        "F1_Score": round(float(f1), 4),
        "ROC_AUC": round(float(auc), 4)
    }
    
    print(f"\n--- Classification Evaluation: {model_name} ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print(f"ROC AUC:   {auc:.4f}")
    
    # Save metrics JSON
    metrics_path = os.path.join(reports_dir, "model_metrics", f"{model_name.lower().replace(' ', '_')}_classification_metrics.json")
    os.makedirs(os.path.dirname(metrics_path), exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)
        
    # Generate Plots
    graphs_dir = os.path.join(reports_dir, "graphs")
    os.makedirs(graphs_dir, exist_ok=True)
    
    # 1. Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["On Time", "Delayed"], yticklabels=["On Time", "Delayed"])
    plt.title(f"Confusion Matrix ({model_name})")
    plt.ylabel("Actual")
    plt.xlabel("Predicted")
    plt.tight_layout()
    plt.savefig(os.path.join(graphs_dir, f"{model_name.lower().replace(' ', '_')}_confusion_matrix.png"))
    plt.close()
    
    # 2. ROC Curve
    try:
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        plt.figure(figsize=(7, 6))
        plt.plot(fpr, tpr, color="#ff9f43", lw=2, label=f"ROC Curve (AUC = {auc:.2f})")
        plt.plot([0, 1], [0, 1], color="gray", lw=1, linestyle="--")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title(f"Receiver Operating Characteristic ({model_name})")
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(os.path.join(graphs_dir, f"{model_name.lower().replace(' ', '_')}_roc_curve.png"))
        plt.close()
    except Exception as e:
        print(f"Failed to generate ROC Curve plot: {e}")
        
    return metrics
