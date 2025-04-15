import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple, Any
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
import joblib
from datetime import datetime

from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file

class ModelDriftDetector:
    """
    ModelDriftDetector monitors and detects drift in model performance over time.

    This class compares a baseline model's performance with current model performance
    to identify potential degradation or drift in model effectiveness.
    """

    def __init__(self,
                 baseline_model_path: str,
                 current_model_path: str,
                 report_dir: str,
                 threshold: float = 0.05):
        """
        Initialize the ModelDriftDetector.

        Args:
            baseline_model_path (str): Path to the baseline model file
            current_model_path (str): Path to the current model file
            report_dir (str): Directory to save drift reports
            threshold (float): Threshold for determining significant drift
        """
        try:
            logging.info("Initializing ModelDriftDetector")
            self.baseline_model_path = baseline_model_path
            self.current_model_path = current_model_path
            self.report_dir = report_dir
            self.threshold = threshold

            # Create report directory if it doesn't exist
            os.makedirs(self.report_dir, exist_ok=True)

            # Load models
            self.baseline_model = self._load_model(baseline_model_path)
            self.current_model = self._load_model(current_model_path)

            logging.info("ModelDriftDetector initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing ModelDriftDetector: {e}")
            raise NetworkSecurityException(e, sys)

    def _load_model(self, model_path: str) -> Any:
        """
        Load a model from a file.

        Args:
            model_path (str): Path to the model file

        Returns:
            Any: Loaded model object
        """
        try:
            logging.info(f"Loading model from {model_path}")
            return joblib.load(model_path)
        except Exception as e:
            logging.error(f"Error loading model from {model_path}: {e}")
            raise NetworkSecurityException(e, sys)

    def calculate_performance_metrics(self,
                                     model: Any,
                                     X: pd.DataFrame,
                                     y: pd.Series) -> Dict[str, float]:
        """
        Calculate performance metrics for a model on given data.

        Args:
            model (Any): Model to evaluate
            X (pd.DataFrame): Feature data
            y (pd.Series): Target data

        Returns:
            Dict[str, float]: Dictionary of performance metrics
        """
        try:
            logging.info("Calculating performance metrics")

            # Make predictions
            y_pred = model.predict(X)
            y_pred_proba = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else None

            # Calculate metrics
            metrics = {
                "accuracy": accuracy_score(y, y_pred),
                "precision": precision_score(y, y_pred, average='weighted'),
                "recall": recall_score(y, y_pred, average='weighted'),
                "f1": f1_score(y, y_pred, average='weighted'),
            }

            # Add AUC if probability predictions are available
            if y_pred_proba is not None:
                try:
                    metrics["auc"] = roc_auc_score(y, y_pred_proba)
                except Exception:
                    metrics["auc"] = None
                    logging.warning("Could not calculate AUC score")

            # Calculate confusion matrix
            cm = confusion_matrix(y, y_pred)
            metrics["confusion_matrix"] = cm.tolist()

            # Get classification report as dictionary
            cr = classification_report(y, y_pred, output_dict=True)
            metrics["classification_report"] = cr

            logging.info("Performance metrics calculated successfully")
            return metrics
        except Exception as e:
            logging.error(f"Error calculating performance metrics: {e}")
            raise NetworkSecurityException(e, sys)

    def detect_model_drift(self,
                          X_baseline: pd.DataFrame,
                          y_baseline: pd.Series,
                          X_current: pd.DataFrame,
                          y_current: pd.Series) -> Dict[str, Any]:
        """
        Detect drift between baseline and current model performance.

        Args:
            X_baseline (pd.DataFrame): Baseline feature data
            y_baseline (pd.Series): Baseline target data
            X_current (pd.DataFrame): Current feature data
            y_current (pd.Series): Current target data

        Returns:
            Dict[str, Any]: Model drift report
        """
        """
        Detect drift between baseline and current model performance.

        Args:
            X_baseline (pd.DataFrame): Baseline feature data
            y_baseline (pd.Series): Baseline target data
            X_current (pd.DataFrame): Current feature data
            y_current (pd.Series): Current target data

        Returns:
            Dict[str, Any]: Model drift report
        """
        try:
            logging.info("Detecting model drift")

            # Calculate performance metrics for both models
            baseline_metrics = self.calculate_performance_metrics(
                self.baseline_model, X_baseline, y_baseline
            )
            current_metrics = self.calculate_performance_metrics(
                self.current_model, X_current, y_current
            )

            # Compare metrics to detect drift
            drift_report = {
                "timestamp": datetime.now().isoformat(),
                "baseline_model_path": self.baseline_model_path,
                "current_model_path": self.current_model_path,
                "baseline_metrics": baseline_metrics,
                "current_metrics": current_metrics,
                "metric_differences": {},
                "drift_detected": False,
                "drift_details": {}
            }

            # Calculate differences and check for drift
            for metric in ["accuracy", "precision", "recall", "f1", "auc"]:
                if metric in baseline_metrics and metric in current_metrics and baseline_metrics[metric] is not None and current_metrics[metric] is not None:
                    diff = current_metrics[metric] - baseline_metrics[metric]
                    drift_report["metric_differences"][metric] = diff

                    # Check if difference exceeds threshold
                    is_significant = abs(diff) > self.threshold
                    is_degradation = diff < 0

                    drift_report["drift_details"][metric] = {
                        "difference": diff,
                        "is_significant": is_significant,
                        "is_degradation": is_degradation,
                        "status": "degraded" if (is_significant and is_degradation) else
                                 "improved" if (is_significant and not is_degradation) else
                                 "stable"
                    }

                    # Update overall drift status
                    if is_significant and is_degradation:
                        drift_report["drift_detected"] = True

            # Generate text report
            text_report = self.generate_text_report(drift_report)

            # Save reports
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            json_report_path = os.path.join(
                self.report_dir,
                f"model_drift_report_{timestamp}.json"
            )
            text_report_path = os.path.join(
                self.report_dir,
                f"model_drift_report_{timestamp}.txt"
            )

            # Save JSON report
            write_yaml_file(json_report_path, drift_report)
            logging.info(f"Model drift JSON report saved to {json_report_path}")

            # Save text report
            with open(text_report_path, 'w') as f:
                f.write(text_report)
            logging.info(f"Model drift text report saved to {text_report_path}")

            # Add report paths to drift report
            drift_report['json_report_path'] = json_report_path
            drift_report['text_report_path'] = text_report_path

            # Generate visualizations if requested
            if os.environ.get('GENERATE_VISUALIZATIONS', 'True').lower() == 'true':
                viz_paths = self.generate_drift_visualizations(drift_report, json_report_path.replace('.json', ''))
                drift_report['visualization_paths'] = viz_paths
            else:
                drift_report['visualization_paths'] = []

            return drift_report
        except Exception as e:
            logging.error(f"Error detecting model drift: {e}")
            raise NetworkSecurityException(e, sys)

    def generate_drift_visualizations(self,
                                     drift_report: Dict[str, Any],
                                     output_prefix: str) -> List[str]:
        """
        Generate visualizations for model drift analysis.

        Args:
            drift_report (Dict[str, Any]): Model drift report
            output_prefix (str): Prefix for output file paths

        Returns:
            List[str]: List of generated visualization file paths
        """
        try:
            logging.info("Generating model drift visualizations")
            visualization_paths = []

            # 1. Metrics comparison bar chart
            plt.figure(figsize=(12, 6))
            metrics = ["accuracy", "precision", "recall", "f1"]
            baseline_values = [drift_report["baseline_metrics"].get(m, 0) for m in metrics]
            current_values = [drift_report["current_metrics"].get(m, 0) for m in metrics]

            x = np.arange(len(metrics))
            width = 0.35

            plt.bar(x - width/2, baseline_values, width, label='Baseline Model')
            plt.bar(x + width/2, current_values, width, label='Current Model')

            plt.xlabel('Metrics')
            plt.ylabel('Score')
            plt.title('Model Performance Comparison')
            plt.xticks(x, metrics)
            plt.legend()
            plt.grid(axis='y', linestyle='--', alpha=0.7)

            metrics_chart_path = f"{output_prefix}_metrics_comparison.png"
            plt.savefig(metrics_chart_path)
            plt.close()
            visualization_paths.append(metrics_chart_path)

            # 2. Confusion matrix heatmaps
            if "confusion_matrix" in drift_report["baseline_metrics"] and "confusion_matrix" in drift_report["current_metrics"]:
                # Baseline confusion matrix
                plt.figure(figsize=(8, 6))
                cm = np.array(drift_report["baseline_metrics"]["confusion_matrix"])
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
                plt.title('Baseline Model Confusion Matrix')
                plt.xlabel('Predicted')
                plt.ylabel('Actual')

                baseline_cm_path = f"{output_prefix}_baseline_confusion_matrix.png"
                plt.savefig(baseline_cm_path)
                plt.close()
                visualization_paths.append(baseline_cm_path)

                # Current confusion matrix
                plt.figure(figsize=(8, 6))
                cm = np.array(drift_report["current_metrics"]["confusion_matrix"])
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
                plt.title('Current Model Confusion Matrix')
                plt.xlabel('Predicted')
                plt.ylabel('Actual')

                current_cm_path = f"{output_prefix}_current_confusion_matrix.png"
                plt.savefig(current_cm_path)
                plt.close()
                visualization_paths.append(current_cm_path)

            # 3. Metric differences chart
            plt.figure(figsize=(10, 6))
            metrics = list(drift_report["metric_differences"].keys())
            differences = list(drift_report["metric_differences"].values())

            colors = ['green' if diff >= 0 else 'red' for diff in differences]

            plt.bar(metrics, differences, color=colors)
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            plt.axhline(y=self.threshold, color='red', linestyle='--', alpha=0.5, label=f'Threshold (+{self.threshold})')
            plt.axhline(y=-self.threshold, color='red', linestyle='--', alpha=0.5, label=f'Threshold (-{self.threshold})')

            plt.xlabel('Metrics')
            plt.ylabel('Difference (Current - Baseline)')
            plt.title('Model Performance Drift')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            plt.legend()

            diff_chart_path = f"{output_prefix}_metric_differences.png"
            plt.savefig(diff_chart_path)
            plt.close()
            visualization_paths.append(diff_chart_path)

            logging.info(f"Generated {len(visualization_paths)} visualizations")
            return visualization_paths
        except Exception as e:
            logging.error(f"Error generating model drift visualizations: {e}")
            raise NetworkSecurityException(e, sys)

    def generate_text_report(self, drift_report: Dict[str, Any]) -> str:
        """
        Generate a text-based model drift report.

        Args:
            drift_report (Dict[str, Any]): Model drift report data

        Returns:
            str: Text-based model drift report
        """
        try:
            logging.info("Generating text-based model drift report")

            # Create report header
            report = [
                "====================================================",
                "               MODEL DRIFT REPORT                ",
                "====================================================",
                f"Report generated: {drift_report['timestamp']}",
                f"Baseline model: {drift_report['baseline_model_path']}",
                f"Current model: {drift_report['current_model_path']}",
                "====================================================",
                ""
            ]

            # Add performance metrics comparison
            report.append("PERFORMANCE METRICS COMPARISON:")
            report.append("-" * 50)
            report.append(f"{'Metric':<15} {'Baseline':<10} {'Current':<10} {'Difference':<10} {'Status':<10}")
            report.append("-" * 50)

            for metric in ["accuracy", "precision", "recall", "f1", "auc"]:
                if metric in drift_report["baseline_metrics"] and metric in drift_report["current_metrics"]:
                    baseline_value = drift_report["baseline_metrics"][metric]
                    current_value = drift_report["current_metrics"][metric]
                    diff = drift_report["metric_differences"][metric]

                    # Determine status
                    status = "N/A"
                    if metric in drift_report["drift_details"]:
                        status = drift_report["drift_details"][metric]["status"]

                    report.append(f"{metric.capitalize():<15} {baseline_value:<10.4f} {current_value:<10.4f} {diff:<+10.4f} {status.capitalize():<10}")

            report.append("-" * 50)
            report.append("")

            # Add drift summary
            report.append("DRIFT SUMMARY:")
            report.append("-" * 50)
            if drift_report["drift_detected"]:
                report.append("⚠️ SIGNIFICANT MODEL DRIFT DETECTED")
                report.append("")
                report.append("The following metrics show significant degradation:")

                significant_degradation = False
                for metric, details in drift_report["drift_details"].items():
                    if details["is_significant"] and details["is_degradation"]:
                        report.append(f"  - {metric.capitalize()}: {details['difference']:<+.4f}")
                        significant_degradation = True

                if not significant_degradation:
                    report.append("  None")
            else:
                report.append("✓ NO SIGNIFICANT MODEL DRIFT DETECTED")
                report.append("")
                report.append("All metrics are within acceptable thresholds.")

            report.append("-" * 50)
            report.append("")

            # Add recommendations
            report.append("RECOMMENDATIONS:")
            report.append("-" * 50)
            if drift_report["drift_detected"]:
                report.append("1. Investigate the cause of model performance degradation")
                report.append("2. Consider retraining the model with more recent data")
                report.append("3. Review feature engineering and preprocessing steps")
                report.append("4. Evaluate if the data distribution has changed significantly")
            else:
                report.append("1. Continue monitoring model performance")
                report.append("2. No immediate action required")

            report.append("-" * 50)
            report.append("")

            # Join report lines
            return "\n".join(report)

        except Exception as e:
            logging.error(f"Error generating text-based model drift report: {e}")
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def get_latest_drift_report(report_dir: str) -> Dict[str, Any]:
        """
        Get the latest model drift report from the report directory.

        Args:
            report_dir (str): Directory containing drift reports

        Returns:
            Dict[str, Any]: Latest model drift report
        """
        try:
            logging.info(f"Getting latest model drift report from {report_dir}")

            # List all report files
            report_files = [
                os.path.join(report_dir, f) for f in os.listdir(report_dir)
                if f.startswith("model_drift_report_") and f.endswith(".json")
            ]

            if not report_files:
                logging.warning("No model drift reports found")
                return None

            # Sort by modification time (newest first)
            latest_report_file = max(report_files, key=os.path.getmtime)
            logging.info(f"Latest report file: {latest_report_file}")

            # Read the report
            report = read_yaml_file(latest_report_file)

            # Get associated visualization files
            prefix = latest_report_file.replace('.json', '')
            visualization_files = [
                f for f in os.listdir(os.path.dirname(latest_report_file))
                if f.startswith(os.path.basename(prefix)) and f.endswith('.png')
            ]

            # Add visualization paths to report
            report["visualization_paths"] = [
                os.path.join(os.path.dirname(latest_report_file), f)
                for f in visualization_files
            ]

            return report
        except Exception as e:
            logging.error(f"Error getting latest model drift report: {e}")
            raise NetworkSecurityException(e, sys)
