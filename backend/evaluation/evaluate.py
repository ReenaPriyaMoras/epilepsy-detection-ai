import os
import sys
import json
import time
import psutil
import torch
import numpy as np
import pandas as pd
from collections import defaultdict
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.epieeg.model import EpiEEGModelLoader
from ml.epieeg.preprocessing import preprocess_edf
from ml.epieeg.explainability import generate_explanation

from .metrics import compute_all_metrics, get_classification_report
from .plots import plot_confusion_matrix, plot_roc_curve, plot_pr_curve, plot_confidence_distribution, plot_explainability_summary

# Constants - recursively scan this folder
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "epieeg", "dataset")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs", "results")

# Setup Reproducibility
torch.manual_seed(42)
np.random.seed(42)

def evaluate_dataset():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    loader = EpiEEGModelLoader.load()
    device = loader.model.bilstm.weight_ih_l0.device
    
    y_true = []
    y_prob = []
    y_pred = []
    
    timing_stats = {"preprocess": [], "inference": [], "xai": [], "total": []}
    memory_stats = []
    cpu_stats = []
    
    global_channel_imp = defaultdict(float)
    global_feature_imp = defaultdict(float)
    
    # 1. Dataset Audit
    all_files = []
    for root, _, files in os.walk(DATASET_DIR):
        for file in files:
            if file.lower().endswith('.edf'):
                all_files.append(os.path.join(root, file))
                
    total_discovered = len(all_files)
    
    # Check for duplicates, labels
    filenames = []
    duplicates = set()
    files_with_labels = 0
    files_without_labels = 0
    
    for filepath in all_files:
        fname = os.path.basename(filepath)
        if fname in filenames:
            duplicates.add(fname)
        filenames.append(fname)
        
        try:
            patient_id = int(fname.split("_")[1].split(".")[0])
            files_with_labels += 1
        except Exception:
            files_without_labels += 1
            
    print("=======================================")
    print("Dataset Audit")
    print("=======================================")
    print(f"Total EDF files discovered : {total_discovered}")
    print(f"Files with labels          : {files_with_labels}")
    print(f"Files without labels       : {files_without_labels}")
    print(f"Duplicate filenames        : {len(duplicates)}")
    print("=======================================\n")
    
    processed_count = 0
    skipped_count = 0
    corrupted_count = 0
    epileptic_count = 0
    normal_count = 0
    
    t_start_pipeline = time.perf_counter()
    
    for i, filepath in enumerate(all_files, 1):
        filename = os.path.basename(filepath)
        
        try:
            patient_id = int(filename.split("_")[1].split(".")[0])
            label = 0 if patient_id <= 30 else 1
        except Exception:
            skipped_count += 1
            continue
            
        print(f"Evaluating...\n{i} / {total_discovered}\n{filename}")
        
        try:
            with open(filepath, "rb") as f:
                file_bytes = f.read()
        except Exception:
            corrupted_count += 1
            continue
            
        t0 = time.perf_counter()
        
        # Track hardware
        process = psutil.Process(os.getpid())
        mem_start = process.memory_info().rss
        cpu_stats.append(psutil.cpu_percent())
        
        try:
            # Preprocessing
            t_pre = time.perf_counter()
            features = preprocess_edf(file_bytes)
            t_pre_end = time.perf_counter()
            
            # Inference
            t_inf = time.perf_counter()
            x = torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(device)
            adj = loader.adj_matrix.to(device)
            with torch.inference_mode():
                output = loader.model(x, adj)
                prob = torch.sigmoid(output).item()
            pred = 1 if prob >= loader.threshold else 0
            t_inf_end = time.perf_counter()
            
            # XAI
            t_xai = time.perf_counter()
            explainability_data = generate_explanation(loader, features, "Epileptic" if pred == 1 else "Non-Epileptic")
            t_xai_end = time.perf_counter()
        except Exception as e:
            corrupted_count += 1
            continue
            
        t_end = time.perf_counter()
        
        timing_stats["preprocess"].append(t_pre_end - t_pre)
        timing_stats["inference"].append(t_inf_end - t_inf)
        timing_stats["xai"].append(t_xai_end - t_xai)
        timing_stats["total"].append(t_end - t0)
        
        # Memory tracking
        mem_end = process.memory_info().rss
        memory_stats.append((mem_end - mem_start) / (1024*1024) if mem_end > mem_start else 0)
        
        y_true.append(label)
        y_prob.append(prob)
        y_pred.append(pred)
        
        if label == 1:
            epileptic_count += 1
        else:
            normal_count += 1
            
        # Aggregate XAI
        if explainability_data:
            for item in explainability_data.get("top_channels", []):
                global_channel_imp[item["name"]] += item["importance"]
            for item in explainability_data.get("top_features", []):
                global_feature_imp[item["name"]] += item["importance"]
                
        processed_count += 1
        elapsed_total = time.perf_counter() - t_start_pipeline
        avg_elapsed = np.mean(timing_stats["total"]) if len(timing_stats["total"]) > 0 else 0
        eta = avg_elapsed * (total_discovered - i)
        
        print(f"Elapsed Time: {elapsed_total:.2f}s\nETA: {eta:.0f}s\nSuccess: {processed_count}\nSkipped: {skipped_count}\nCorrupted: {corrupted_count}\n")

    # Evaluation Accounting Validation
    total_accounted = processed_count + skipped_count + corrupted_count
    if total_accounted != total_discovered:
        print(f"CRITICAL ERROR: Dataset accounting mismatch! Total accounted: {total_accounted} != Total discovered: {total_discovered}. Terminating.")
        sys.exit(1)
        
    completion_rate = (processed_count / total_discovered) * 100 if total_discovered > 0 else 0.0

    print("\nDataset Summary")
    print(f"Total EDF discovered : {total_discovered}")
    print(f"Successfully evaluated : {processed_count}")
    print(f"Skipped : {skipped_count}")
    print(f"Corrupted : {corrupted_count}")
    print(f"Completion Rate : {completion_rate:.2f}%")
    
    if processed_count == 0:
        print("No files were successfully processed. Exiting.")
        return
    
    # Average out XAI scores
    for k in global_channel_imp:
        global_channel_imp[k] /= processed_count
    for k in global_feature_imp:
        global_feature_imp[k] /= processed_count
        
    # Metrics
    metrics_dict = compute_all_metrics(y_true, y_prob, y_pred)
    class_report = get_classification_report(y_true, y_pred)
    
    # Statistical Summary
    prob_arr = np.array(y_prob)
    stats_summary = {
        "Mean Confidence": float(np.mean(prob_arr)),
        "Median Confidence": float(np.median(prob_arr)),
        "Standard Deviation": float(np.std(prob_arr)),
        "Minimum Confidence": float(np.min(prob_arr)),
        "Maximum Confidence": float(np.max(prob_arr))
    }
    metrics_dict.update(stats_summary)
    
    perf_summary = {
        "Average Preprocessing Time (s)": float(np.mean(timing_stats["preprocess"])),
        "Average Inference Time (s)": float(np.mean(timing_stats["inference"])),
        "Average Explainability Time (s)": float(np.mean(timing_stats["xai"])),
        "Average Total Response Time (s)": float(np.mean(timing_stats["total"])),
        "Minimum Processing Time (s)": float(np.min(timing_stats["total"])),
        "Maximum Processing Time (s)": float(np.max(timing_stats["total"])),
        "Standard Deviation Time (s)": float(np.std(timing_stats["total"])),
        "Peak Memory Spike (MB)": float(np.max(memory_stats)),
        "Average CPU Usage (%)": float(np.mean(cpu_stats))
    }
    
    dataset_summary = {
        "total_discovered": total_discovered,
        "successfully_evaluated": processed_count,
        "skipped": skipped_count,
        "corrupted": corrupted_count,
        "completion_rate": completion_rate
    }
    
    final_json = {
        "dataset": dataset_summary,
        "performance": perf_summary,
        "metrics": metrics_dict
    }
    
    # Save Metrics JSON
    with open(os.path.join(RESULTS_DIR, "evaluation_results.json"), "w") as f:
        json.dump(final_json, f, indent=4)
        
    # Save Metrics CSV (One row per metric)
    csv_rows = []
    csv_rows.append({"Metric": "Total EDF Discovered", "Value": total_discovered})
    csv_rows.append({"Metric": "Successfully Evaluated", "Value": processed_count})
    csv_rows.append({"Metric": "Skipped", "Value": skipped_count})
    csv_rows.append({"Metric": "Corrupted", "Value": corrupted_count})
    csv_rows.append({"Metric": "Completion Rate", "Value": completion_rate})
    for k, v in metrics_dict.items():
        csv_rows.append({"Metric": k, "Value": v})
    pd.DataFrame(csv_rows).to_csv(os.path.join(RESULTS_DIR, "evaluation_metrics.csv"), index=False)
    
    # Save Classification Report
    with open(os.path.join(RESULTS_DIR, "classification_report.txt"), "w") as f:
        f.write(class_report)
        
    # Plots
    plot_confusion_matrix(y_true, y_pred, RESULTS_DIR)
    plot_roc_curve(y_true, y_prob, RESULTS_DIR)
    plot_pr_curve(y_true, y_prob, RESULTS_DIR)
    plot_confidence_distribution(y_true, y_prob, RESULTS_DIR)
    plot_explainability_summary(global_channel_imp, global_feature_imp, RESULTS_DIR)
    
    # Generate Markdown Report
    from .report import generate_markdown_report
    generate_markdown_report(metrics_dict, perf_summary, class_report, dataset_summary, RESULTS_DIR)
    print("\nEvaluation completed. Results saved to docs/results/")

if __name__ == "__main__":
    evaluate_dataset()
