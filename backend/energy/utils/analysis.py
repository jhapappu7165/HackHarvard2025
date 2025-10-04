import numpy as np
from typing import List, Dict, Tuple
from scipy import stats

class EnergyAnalyzer:
    
    @staticmethod
    def calculate_efficiency(usage: float, square_feet: int) -> float:
        """Calculate kBTU per square foot"""
        # Convert to BTU (simplified - actual conversion varies by fuel type)
        btu = usage * 3.412  # kWh to BTU conversion
        return (btu / square_feet) if square_feet > 0 else 0
    
    @staticmethod
    def detect_anomalies(readings: List[Dict]) -> List[int]:
        """Detect unusual energy usage using statistical methods"""
        if len(readings) < 6:
            return []
        
        usages = [r['usage'] for r in readings]
        mean = np.mean(usages)
        std = np.std(usages)
        
        # Detect outliers (values beyond 2 standard deviations)
        anomalies = []
        for idx, usage in enumerate(usages):
            z_score = abs((usage - mean) / std) if std > 0 else 0
            if z_score > 2:
                anomalies.append(idx)
        
        return anomalies
    
    @staticmethod
    def calculate_trend(readings: List[Dict]) -> Tuple[str, float]:
        """Calculate energy usage trend"""
        if len(readings) < 6:
            return "insufficient_data", 0
        
        usages = [r['usage'] for r in readings]
        x = np.arange(len(usages))
        
        # Linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, usages)
        
        # Determine trend
        if abs(slope) < np.mean(usages) * 0.01:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Percent change
        percent_change = (slope * len(usages) / np.mean(usages)) * 100
        
        return trend, percent_change
    
    @staticmethod
    def compare_to_baseline(current_usage: float, baseline_usage: float) -> Dict:
        """Compare current usage to baseline"""
        if baseline_usage == 0:
            return {'change': 0, 'percent_change': 0}
        
        change = current_usage - baseline_usage
        percent_change = (change / baseline_usage) * 100
        
        return {
            'change': round(change, 2),
            'percent_change': round(percent_change, 2)
        }
    
    @staticmethod
    def calculate_rolling_sum(readings: List[Dict], window: int = 12) -> List[float]:
        """Calculate 12-month rolling sum"""
        usages = [r['usage'] for r in readings]
        rolling_sums = []
        
        for i in range(len(usages)):
            start_idx = max(0, i - window + 1)
            rolling_sums.append(sum(usages[start_idx:i+1]))
        
        return rolling_sums