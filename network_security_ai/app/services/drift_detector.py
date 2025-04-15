import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DriftDetector:
    """Service for detecting data drift in network traffic"""
    
    def __init__(self, baseline_data: np.ndarray, feature_names: List[str], sensitivity: float = 0.05):
        """Initialize with baseline network traffic data"""
        self.baseline_distribution = self._compute_distribution(baseline_data)
        self.feature_names = feature_names
        self.sensitivity = sensitivity
        self.drift_history = []
        logger.info(f"Drift detector initialized with {len(feature_names)} features")
        
    def _compute_distribution(self, data: np.ndarray) -> Dict:
        """Compute statistical distribution of network traffic features"""
        # Simple implementation using mean and standard deviation
        distribution = {
            'mean': np.mean(data, axis=0),
            'std': np.std(data, axis=0),
            'min': np.min(data, axis=0),
            'max': np.max(data, axis=0)
        }
        return distribution
        
    def detect_drift(self, current_data: np.ndarray) -> Tuple[bool, Optional[Dict]]:
        """Detect if current data has drifted from baseline"""
        current_distribution = self._compute_distribution(current_data)
        
        # Calculate drift score using normalized Euclidean distance between means
        mean_diff = current_distribution['mean'] - self.baseline_distribution['mean']
        normalized_diff = mean_diff / (self.baseline_distribution['std'] + 1e-10)  # Avoid division by zero
        drift_score = np.sqrt(np.mean(normalized_diff ** 2))
        
        drift_detected = drift_score > self.sensitivity
        
        if drift_detected:
            # Identify which features have drifted the most
            feature_drift_scores = np.abs(normalized_diff)
            drifted_features_indices = np.where(feature_drift_scores > self.sensitivity)[0]
            drifted_features = [self.feature_names[i] for i in drifted_features_indices]
            
            # Calculate severity based on drift score
            severity = self._calculate_severity(drift_score)
            
            drift_info = {
                "timestamp": datetime.now(),
                "drift_score": float(drift_score),
                "features": drifted_features,
                "severity": severity,
                "feature_drift_scores": {
                    self.feature_names[i]: float(feature_drift_scores[i]) 
                    for i in range(len(self.feature_names))
                }
            }
            
            self.drift_history.append(drift_info)
            logger.warning(f"Drift detected with score {drift_score:.4f}, severity: {severity}")
            
            return True, drift_info
        
        logger.info(f"No significant drift detected (score: {drift_score:.4f})")
        return False, None
        
    def _calculate_severity(self, drift_score: float) -> str:
        """Calculate severity level based on drift score"""
        if drift_score > 0.5:
            return "Critical"
        elif drift_score > 0.3:
            return "High"
        elif drift_score > 0.1:
            return "Medium"
        else:
            return "Low"
            
    def update_baseline(self, new_baseline_data: np.ndarray) -> None:
        """Update the baseline distribution with new data"""
        self.baseline_distribution = self._compute_distribution(new_baseline_data)
        logger.info("Baseline distribution updated")
