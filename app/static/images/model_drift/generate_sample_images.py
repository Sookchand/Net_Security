import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set the style
plt.style.use('ggplot')
sns.set_theme(style="whitegrid")

# Create metrics comparison chart
def create_metrics_comparison():
    plt.figure(figsize=(12, 6))
    metrics = ["Accuracy", "Precision", "Recall", "F1"]
    baseline_values = [0.92, 0.89, 0.87, 0.88]
    current_values = [0.90, 0.86, 0.85, 0.85]
    
    x = np.arange(len(metrics))
    width = 0.35
    
    plt.bar(x - width/2, baseline_values, width, label='Baseline Model', color='#4e73df')
    plt.bar(x + width/2, current_values, width, label='Current Model', color='#1cc88a')
    
    plt.xlabel('Metrics', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.title('Model Performance Comparison', fontsize=14, fontweight='bold')
    plt.xticks(x, metrics, fontsize=11)
    plt.ylim(0.8, 1.0)
    plt.legend(fontsize=11)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    for i, v in enumerate(baseline_values):
        plt.text(i - width/2, v + 0.01, f'{v:.2f}', ha='center', fontsize=10)
    
    for i, v in enumerate(current_values):
        plt.text(i + width/2, v + 0.01, f'{v:.2f}', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('metrics_comparison.png', dpi=100)
    plt.close()

# Create confusion matrices
def create_confusion_matrices():
    # Baseline confusion matrix
    plt.figure(figsize=(8, 6))
    cm = np.array([
        [450, 30, 15, 5],
        [25, 380, 10, 5],
        [10, 15, 320, 5],
        [5, 5, 10, 230]
    ])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True)
    plt.title('Baseline Model Confusion Matrix', fontsize=14, fontweight='bold')
    plt.xlabel('Predicted', fontsize=12)
    plt.ylabel('Actual', fontsize=12)
    plt.tight_layout()
    plt.savefig('baseline_confusion_matrix.png', dpi=100)
    plt.close()
    
    # Current confusion matrix
    plt.figure(figsize=(8, 6))
    cm = np.array([
        [440, 35, 20, 5],
        [30, 370, 15, 5],
        [15, 20, 310, 5],
        [10, 5, 15, 220]
    ])
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=True)
    plt.title('Current Model Confusion Matrix', fontsize=14, fontweight='bold')
    plt.xlabel('Predicted', fontsize=12)
    plt.ylabel('Actual', fontsize=12)
    plt.tight_layout()
    plt.savefig('current_confusion_matrix.png', dpi=100)
    plt.close()

# Create metric differences chart
def create_metric_differences():
    plt.figure(figsize=(10, 6))
    metrics = ["Accuracy", "Precision", "Recall", "F1", "AUC"]
    differences = [-0.02, -0.03, -0.02, -0.03, -0.01]
    
    colors = ['#e74a3b' if diff < 0 else '#1cc88a' for diff in differences]
    
    plt.bar(metrics, differences, color=colors)
    plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    plt.axhline(y=0.05, color='red', linestyle='--', alpha=0.5, label='Threshold (+0.05)')
    plt.axhline(y=-0.05, color='red', linestyle='--', alpha=0.5, label='Threshold (-0.05)')
    
    plt.xlabel('Metrics', fontsize=12)
    plt.ylabel('Difference (Current - Baseline)', fontsize=12)
    plt.title('Model Performance Drift', fontsize=14, fontweight='bold')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(fontsize=11)
    
    for i, v in enumerate(differences):
        plt.text(i, v + (0.005 if v < 0 else -0.005), 
                f'{v:.3f}', ha='center', va='bottom' if v < 0 else 'top',
                fontsize=10, fontweight='bold', color='white')
    
    plt.tight_layout()
    plt.savefig('metric_differences.png', dpi=100)
    plt.close()

if __name__ == "__main__":
    # Generate all images
    create_metrics_comparison()
    create_confusion_matrices()
    create_metric_differences()
    
    print("Sample model drift images generated successfully!")
