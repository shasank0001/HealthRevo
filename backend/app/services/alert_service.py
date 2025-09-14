from typing import List, Dict, Optional
from datetime import datetime, timedelta
import statistics
from app.models.vitals import Vitals
from app.models.alert import Alert, AlertSeverity, AlertType
from app.config import settings


class AnomalyDetector:
    """Detects anomalies in vital signs and generates alerts."""
    
    @staticmethod
    def check_vitals_anomalies(new_vital: Vitals, historical_vitals: List[Vitals]) -> List[Dict]:
        """Check for anomalies in new vital signs compared to historical data."""
        
        alerts = []
        
        # Immediate emergency thresholds
        emergency_alerts = AnomalyDetector._check_emergency_thresholds(new_vital)
        alerts.extend(emergency_alerts)
        
        # Statistical anomalies (require historical data)
        if len(historical_vitals) >= 3:  # Need minimum data for comparison
            statistical_alerts = AnomalyDetector._check_statistical_anomalies(
                new_vital, historical_vitals
            )
            alerts.extend(statistical_alerts)
        
        return alerts
    
    @staticmethod
    def _check_emergency_thresholds(vital: Vitals) -> List[Dict]:
        """Check for immediate medical emergency thresholds."""
        
        alerts = []
        
        # Blood pressure emergencies
        if vital.systolic and vital.systolic > 180:
            alerts.append({
                "severity": AlertSeverity.URGENT,
                "type": AlertType.VITAL_EMERGENCY,
                "title": "Hypertensive Crisis",
                "message": f"Systolic blood pressure critically high: {vital.systolic} mmHg",
                "recommendation": "Seek immediate medical attention",
                "alert_metadata": {"vital_type": "systolic_bp", "value": vital.systolic}
            })
        
        if vital.diastolic and vital.diastolic > 120:
            alerts.append({
                "severity": AlertSeverity.URGENT,
                "type": AlertType.VITAL_EMERGENCY,
                "title": "Diastolic Hypertensive Crisis",
                "message": f"Diastolic blood pressure critically high: {vital.diastolic} mmHg",
                "recommendation": "Seek immediate medical attention",
                "alert_metadata": {"vital_type": "diastolic_bp", "value": vital.diastolic}
            })
        
        # Heart rate emergencies
        if vital.heart_rate:
            if vital.heart_rate > 120:
                alerts.append({
                    "severity": AlertSeverity.SERIOUS,
                    "type": AlertType.VITAL_EMERGENCY,
                    "title": "Tachycardia Detected",
                    "message": f"Heart rate elevated: {vital.heart_rate} BPM",
                    "recommendation": "Monitor closely and consult healthcare provider",
                    "alert_metadata": {"vital_type": "heart_rate", "value": vital.heart_rate}
                })
            elif vital.heart_rate < 50:
                alerts.append({
                    "severity": AlertSeverity.SERIOUS,
                    "type": AlertType.VITAL_EMERGENCY,
                    "title": "Bradycardia Detected",
                    "message": f"Heart rate low: {vital.heart_rate} BPM",
                    "recommendation": "Monitor closely and consult healthcare provider",
                    "alert_metadata": {"vital_type": "heart_rate", "value": vital.heart_rate}
                })
        
        # Oxygen saturation
        if vital.oxygen_saturation:
            if vital.oxygen_saturation < 90:
                alerts.append({
                    "severity": AlertSeverity.URGENT,
                    "type": AlertType.VITAL_EMERGENCY,
                    "title": "Low Oxygen Saturation",
                    "message": f"Oxygen saturation critically low: {vital.oxygen_saturation}%",
                    "recommendation": "Seek immediate medical attention",
                    "alert_metadata": {"vital_type": "oxygen_saturation", "value": vital.oxygen_saturation}
                })
            elif vital.oxygen_saturation < 95:
                alerts.append({
                    "severity": AlertSeverity.SERIOUS,
                    "type": AlertType.VITAL_EMERGENCY,
                    "title": "Reduced Oxygen Saturation",
                    "message": f"Oxygen saturation below normal: {vital.oxygen_saturation}%",
                    "recommendation": "Monitor closely and consider medical consultation",
                    "alert_metadata": {"vital_type": "oxygen_saturation", "value": vital.oxygen_saturation}
                })
        
        # Blood glucose emergencies
        if vital.blood_glucose:
            if vital.blood_glucose > 300:
                alerts.append({
                    "severity": AlertSeverity.URGENT,
                    "type": AlertType.VITAL_EMERGENCY,
                    "title": "Severe Hyperglycemia",
                    "message": f"Blood glucose dangerously high: {vital.blood_glucose} mg/dL",
                    "recommendation": "Seek immediate medical attention",
                    "alert_metadata": {"vital_type": "blood_glucose", "value": vital.blood_glucose}
                })
            elif vital.blood_glucose < 70:
                alerts.append({
                    "severity": AlertSeverity.URGENT,
                    "type": AlertType.VITAL_EMERGENCY,
                    "title": "Hypoglycemia",
                    "message": f"Blood glucose low: {vital.blood_glucose} mg/dL",
                    "recommendation": "Consume fast-acting carbohydrates and monitor",
                    "alert_metadata": {"vital_type": "blood_glucose", "value": vital.blood_glucose}
                })
        
        # Temperature
        if vital.temperature:
            if vital.temperature > 39.0:  # 102.2°F
                alerts.append({
                    "severity": AlertSeverity.SERIOUS,
                    "type": AlertType.VITAL_EMERGENCY,
                    "title": "High Fever",
                    "message": f"Temperature elevated: {vital.temperature}°C",
                    "recommendation": "Monitor temperature and consider medical consultation",
                    "alert_metadata": {"vital_type": "temperature", "value": vital.temperature}
                })
            elif vital.temperature < 35.0:  # 95°F
                alerts.append({
                    "severity": AlertSeverity.SERIOUS,
                    "type": AlertType.VITAL_EMERGENCY,
                    "title": "Hypothermia Risk",
                    "message": f"Temperature low: {vital.temperature}°C",
                    "recommendation": "Seek warming measures and medical attention",
                    "alert_metadata": {"vital_type": "temperature", "value": vital.temperature}
                })
        
        return alerts
    
    @staticmethod
    def _check_statistical_anomalies(new_vital: Vitals, historical_vitals: List[Vitals]) -> List[Dict]:
        """Check for statistical anomalies based on historical patterns."""
        
        alerts = []
        threshold_percentage = settings.anomaly_threshold_percentage / 100
        
        # Check each vital sign for anomalies
        vital_checks = [
            ("systolic", "Systolic Blood Pressure", "mmHg"),
            ("diastolic", "Diastolic Blood Pressure", "mmHg"),
            ("heart_rate", "Heart Rate", "BPM"),
            ("temperature", "Temperature", "°C"),
            ("blood_glucose", "Blood Glucose", "mg/dL"),
            ("oxygen_saturation", "Oxygen Saturation", "%")
        ]
        
        for vital_attr, display_name, unit in vital_checks:
            current_value = getattr(new_vital, vital_attr)
            if current_value is None:
                continue
            
            # Get historical values for this vital sign
            historical_values = [
                getattr(v, vital_attr) for v in historical_vitals
                if getattr(v, vital_attr) is not None
            ]
            
            if len(historical_values) < 3:
                continue
            
            # Calculate statistics
            mean_value = statistics.mean(historical_values)
            
            # Check for significant deviation
            if mean_value > 0:  # Avoid division by zero
                deviation_percentage = abs(current_value - mean_value) / mean_value
                
                if deviation_percentage > threshold_percentage:
                    direction = "increased" if current_value > mean_value else "decreased"
                    percentage_change = int(deviation_percentage * 100)
                    
                    alerts.append({
                        "severity": AlertSeverity.MILD,
                        "type": AlertType.ANOMALY,
                        "title": f"{display_name} Anomaly",
                        "message": f"{display_name} {direction} by {percentage_change}% from recent average: {current_value} {unit}",
                        "recommendation": "Monitor trend and consult healthcare provider if pattern continues",
                        "alert_metadata": {
                            "vital_type": vital_attr,
                            "current_value": current_value,
                            "historical_mean": round(mean_value, 2),
                            "deviation_percentage": round(deviation_percentage * 100, 1)
                        }
                    })
        
        return alerts
