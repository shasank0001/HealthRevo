from typing import List, Dict, Optional
from datetime import datetime, timedelta
import statistics
from app.models.vitals import Vitals
from app.config import settings


class RiskCalculator:
    """Heuristic-based risk calculation engine."""
    
    @staticmethod
    def calculate_hypertension_risk(vitals_list: List[Vitals]) -> Dict:
        """Calculate hypertension risk based on blood pressure readings."""
        
        if not vitals_list:
            return {
                "score": 0,
                "risk_level": "low",
                "drivers": {"data_availability": "insufficient"},
                "confidence": 0
            }
        
        # Filter valid BP readings
        bp_readings = [
            (v.systolic, v.diastolic) 
            for v in vitals_list 
            if v.systolic and v.diastolic
        ]
        
        if not bp_readings:
            return {
                "score": 0,
                "risk_level": "low", 
                "drivers": {"blood_pressure": "no_data"},
                "confidence": 0
            }
        
        # Calculate averages
        systolic_values = [bp[0] for bp in bp_readings]
        diastolic_values = [bp[1] for bp in bp_readings]
        
        avg_systolic = statistics.mean(systolic_values)
        avg_diastolic = statistics.mean(diastolic_values)
        
        # Risk scoring based on AHA guidelines
        systolic_score = max(0, (avg_systolic - 120) * 1.2)
        diastolic_score = max(0, (avg_diastolic - 80) * 1.5)
        
        # Combined score (0-100)
        raw_score = systolic_score + diastolic_score
        score = min(100, max(0, raw_score))
        
        # Risk categorization
        if score < 20:
            risk_level = "low"
        elif score < 50:
            risk_level = "moderate"
        elif score < 80:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Identify drivers
        drivers = {
            "avg_systolic": round(avg_systolic, 1),
            "avg_diastolic": round(avg_diastolic, 1),
            "readings_count": len(bp_readings)
        }
        
        if avg_systolic > 140:
            drivers["high_systolic"] = True
        if avg_diastolic > 90:
            drivers["high_diastolic"] = True
        
        # Confidence based on data quality
        confidence = min(100, len(bp_readings) * 20)  # More readings = higher confidence
        
        return {
            "score": round(score, 2),
            "risk_level": risk_level,
            "drivers": drivers,
            "confidence": confidence,
            "recommendations": RiskCalculator._get_hypertension_recommendations(score, drivers)
        }
    
    @staticmethod
    def calculate_diabetes_risk(vitals_list: List[Vitals]) -> Dict:
        """Calculate diabetes risk based on blood glucose readings."""
        
        glucose_readings = [
            v.blood_glucose 
            for v in vitals_list 
            if v.blood_glucose is not None
        ]
        
        if not glucose_readings:
            return {
                "score": 0,
                "risk_level": "low",
                "drivers": {"blood_glucose": "no_data"},
                "confidence": 0
            }
        
        avg_glucose = statistics.mean(glucose_readings)
        max_glucose = max(glucose_readings)
        
        # Risk scoring based on ADA guidelines
        if avg_glucose < 100:
            score = 0
        elif avg_glucose < 126:
            score = 30 + (avg_glucose - 100) * 1.5  # Prediabetes range
        else:
            score = 70 + min(30, (avg_glucose - 126) * 0.5)  # Diabetes range
        
        # Consider maximum reading
        if max_glucose > 200:
            score = max(score, 80)  # Random glucose over 200 mg/dL
        
        score = min(100, max(0, score))
        
        # Risk categorization
        if score < 25:
            risk_level = "low"
        elif score < 50:
            risk_level = "moderate"
        elif score < 75:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        drivers = {
            "avg_glucose": round(avg_glucose, 1),
            "max_glucose": round(max_glucose, 1),
            "readings_count": len(glucose_readings)
        }
        
        confidence = min(100, len(glucose_readings) * 25)
        
        return {
            "score": round(score, 2),
            "risk_level": risk_level,
            "drivers": drivers,
            "confidence": confidence,
            "recommendations": RiskCalculator._get_diabetes_recommendations(score, drivers)
        }
    
    @staticmethod
    def _get_hypertension_recommendations(score: float, drivers: Dict) -> List[str]:
        """Get recommendations for hypertension management."""
        recommendations = []
        
        if score > 50:
            recommendations.append("Monitor blood pressure daily")
            recommendations.append("Reduce sodium intake")
            recommendations.append("Increase physical activity")
        
        if score > 75:
            recommendations.append("Consult healthcare provider immediately")
            recommendations.append("Consider medication review")
        
        return recommendations
    
    @staticmethod
    def _get_diabetes_recommendations(score: float, drivers: Dict) -> List[str]:
        """Get recommendations for diabetes management."""
        recommendations = []
        
        if score > 30:
            recommendations.append("Monitor blood glucose regularly")
            recommendations.append("Follow diabetic diet guidelines")
            recommendations.append("Maintain regular exercise routine")
        
        if score > 70:
            recommendations.append("Urgent medical consultation required")
            recommendations.append("Review medication adherence")
        
        return recommendations
