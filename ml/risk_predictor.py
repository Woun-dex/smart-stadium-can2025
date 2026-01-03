"""
Stadium Risk Prediction Model
=============================
ML-based congestion risk prediction for proactive crowd management.
Provides real-time predictions and recommendations.
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum


class RiskLevel(Enum):
    """Risk severity levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ActionType(Enum):
    """Types of control actions."""
    NONE = "none"
    OPEN_SECURITY = "open_security"
    OPEN_ENTRY = "open_entry"
    OPEN_EXIT = "open_exit"
    OPEN_VENDORS = "open_vendors"
    ENABLE_REDIRECT = "enable_redirect"
    THROTTLE = "throttle"


@dataclass
class Prediction:
    """Risk prediction result."""
    risk_score: float
    risk_level: RiskLevel
    risk_type: str  # "ENTRY" or "EXIT"
    predicted_wait: float
    predicted_queue: int
    confidence: float
    time_to_critical: Optional[float]  # Minutes until critical if no action


@dataclass
class Recommendation:
    """Action recommendation."""
    action: ActionType
    priority: str  # "low", "medium", "high", "urgent"
    description: str
    expected_improvement: float  # Percentage improvement expected
    gates_to_open: int


class StadiumRiskPredictor:
    """
    ML-based risk prediction for stadium crowd management.
    
    Uses historical patterns and real-time metrics to predict:
    - Entry congestion risk
    - Exit congestion risk
    - Optimal resource allocation
    - Proactive interventions
    """
    
    # Configuration thresholds
    QUEUE_CRITICAL = 5000
    QUEUE_HIGH = 3000
    QUEUE_MODERATE = 1500
    
    WAIT_CRITICAL = 25  # minutes
    WAIT_HIGH = 15
    WAIT_MODERATE = 8
    
    EXIT_QUEUE_CRITICAL = 3000
    EXIT_QUEUE_HIGH = 1500
    EXIT_WAIT_CRITICAL = 20
    
    def __init__(self, kickoff_time: int = 180):
        """
        Initialize the risk predictor.
        
        Args:
            kickoff_time: Time of match kickoff in simulation minutes
        """
        self.kickoff_time = kickoff_time
        self.match_end_time = kickoff_time + 120  # ~2 hours match
        self.history: List[Dict] = []
        
    def predict_risk(
        self,
        current_time: float,
        security_queue: int,
        turnstile_queue: int,
        exit_queue: int,
        avg_security_wait: float,
        avg_turnstile_wait: float,
        avg_exit_wait: float,
        arrival_rate: float,
        exit_rate: float,
        fans_in_stadium: int,
        stadium_capacity: int = 68000
    ) -> Tuple[Prediction, Prediction]:
        """
        Predict entry and exit congestion risk.
        
        Returns:
            Tuple of (entry_prediction, exit_prediction)
        """
        # Calculate entry risk
        entry_queue = security_queue + turnstile_queue
        entry_wait = avg_security_wait + avg_turnstile_wait
        
        entry_pred = self._calculate_entry_risk(
            current_time, entry_queue, entry_wait, arrival_rate
        )
        
        # Calculate exit risk
        exit_pred = self._calculate_exit_risk(
            current_time, exit_queue, avg_exit_wait, exit_rate, fans_in_stadium
        )
        
        # Store in history
        self.history.append({
            'time': current_time,
            'entry_risk': entry_pred.risk_score,
            'exit_risk': exit_pred.risk_score,
            'entry_queue': entry_queue,
            'exit_queue': exit_queue
        })
        
        return entry_pred, exit_pred
    
    def _calculate_entry_risk(
        self,
        current_time: float,
        queue: int,
        wait: float,
        arrival_rate: float
    ) -> Prediction:
        """Calculate entry congestion risk."""
        
        # Queue-based risk (0-1)
        queue_risk = min(1.0, queue / self.QUEUE_CRITICAL)
        
        # Wait-based risk (0-1)
        wait_risk = min(1.0, wait / self.WAIT_CRITICAL)
        
        # Time pressure (higher closer to kickoff)
        time_risk = 0.0
        if current_time < self.kickoff_time:
            time_remaining = self.kickoff_time - current_time
            if time_remaining < 30:
                time_risk = 0.4  # Very urgent
            elif time_remaining < 60:
                time_risk = 0.2
            elif time_remaining < 90:
                time_risk = 0.1
        
        # Trend risk (if queue is growing fast)
        trend_risk = 0.0
        if len(self.history) >= 5:
            recent_queues = [h['entry_queue'] for h in self.history[-5:]]
            if len(recent_queues) >= 2:
                queue_growth = recent_queues[-1] - recent_queues[0]
                if queue_growth > 500:
                    trend_risk = min(0.3, queue_growth / 2000)
        
        # Combined risk score
        risk_score = (
            queue_risk * 0.35 +
            wait_risk * 0.35 +
            time_risk * 0.15 +
            trend_risk * 0.15
        )
        
        # Determine risk level
        risk_level = self._score_to_level(risk_score)
        
        # Estimate time to critical
        time_to_critical = None
        if arrival_rate > 0 and risk_score < 0.8:
            queue_to_critical = max(0, self.QUEUE_CRITICAL - queue)
            time_to_critical = queue_to_critical / max(arrival_rate, 1) * 0.5
        
        # Calculate confidence (higher with more history)
        confidence = min(0.95, 0.6 + len(self.history) * 0.01)
        
        return Prediction(
            risk_score=round(risk_score, 3),
            risk_level=risk_level,
            risk_type="ENTRY",
            predicted_wait=round(wait * (1 + risk_score * 0.5), 1),
            predicted_queue=int(queue * (1 + risk_score * 0.3)),
            confidence=round(confidence, 2),
            time_to_critical=round(time_to_critical, 1) if time_to_critical else None
        )
    
    def _calculate_exit_risk(
        self,
        current_time: float,
        queue: int,
        wait: float,
        exit_rate: float,
        fans_in_stadium: int
    ) -> Prediction:
        """Calculate exit congestion risk."""
        
        # Queue-based risk (0-1)
        queue_risk = min(1.0, queue / self.EXIT_QUEUE_CRITICAL)
        
        # Wait-based risk (0-1)
        wait_risk = min(1.0, wait / self.EXIT_WAIT_CRITICAL)
        
        # Time-based risk (higher after match ends)
        time_risk = 0.0
        if current_time > self.match_end_time:
            time_since_end = current_time - self.match_end_time
            if time_since_end < 15:
                time_risk = 0.5  # Peak exit rush
            elif time_since_end < 30:
                time_risk = 0.4
            elif time_since_end < 60:
                time_risk = 0.2
        elif current_time > self.kickoff_time + 90:  # Halftime onwards
            time_risk = 0.15
        
        # Anticipation risk (many fans still inside = exit rush coming)
        anticipation_risk = 0.0
        if current_time > self.kickoff_time + 90 and fans_in_stadium > 30000:
            anticipation_risk = min(0.3, fans_in_stadium / 100000)
        
        # Combined risk score
        risk_score = (
            queue_risk * 0.30 +
            wait_risk * 0.35 +
            time_risk * 0.20 +
            anticipation_risk * 0.15
        )
        
        # Determine risk level
        risk_level = self._score_to_level(risk_score)
        
        # Confidence
        confidence = min(0.95, 0.6 + len(self.history) * 0.01)
        
        return Prediction(
            risk_score=round(risk_score, 3),
            risk_level=risk_level,
            risk_type="EXIT",
            predicted_wait=round(wait * (1 + risk_score * 0.5), 1),
            predicted_queue=int(queue * (1 + risk_score * 0.3)),
            confidence=round(confidence, 2),
            time_to_critical=None
        )
    
    def _score_to_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level."""
        if score >= 0.75:
            return RiskLevel.CRITICAL
        elif score >= 0.55:
            return RiskLevel.HIGH
        elif score >= 0.35:
            return RiskLevel.MODERATE
        else:
            return RiskLevel.LOW
    
    def get_recommendations(
        self,
        entry_pred: Prediction,
        exit_pred: Prediction,
        current_resources: Dict
    ) -> List[Recommendation]:
        """
        Generate action recommendations based on predictions.
        
        Args:
            entry_pred: Entry risk prediction
            exit_pred: Exit risk prediction
            current_resources: Dict with current resource counts
            
        Returns:
            List of recommended actions, sorted by priority
        """
        recommendations = []
        
        # Determine primary risk
        if exit_pred.risk_score > entry_pred.risk_score and exit_pred.risk_score > 0.35:
            # Exit is priority
            recs = self._exit_recommendations(exit_pred, current_resources)
            recommendations.extend(recs)
        
        if entry_pred.risk_score > 0.35:
            # Entry needs attention
            recs = self._entry_recommendations(entry_pred, current_resources)
            recommendations.extend(recs)
        
        # Sort by priority
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 4))
        
        return recommendations
    
    def _entry_recommendations(
        self, pred: Prediction, resources: Dict
    ) -> List[Recommendation]:
        """Generate entry-specific recommendations."""
        recs = []
        
        current_security = resources.get('active_security', 30)
        max_security = resources.get('max_security', 80)
        current_turnstiles = resources.get('active_turnstiles', 20)
        max_turnstiles = resources.get('max_turnstiles', 60)
        
        if pred.risk_level == RiskLevel.CRITICAL:
            # Urgent actions
            security_to_open = min(10, max_security - current_security)
            if security_to_open > 0:
                recs.append(Recommendation(
                    action=ActionType.OPEN_SECURITY,
                    priority="urgent",
                    description=f"🚨 URGENT: Open {security_to_open} additional security lanes immediately",
                    expected_improvement=25.0,
                    gates_to_open=security_to_open
                ))
            
            recs.append(Recommendation(
                action=ActionType.ENABLE_REDIRECT,
                priority="urgent",
                description="🚨 Enable queue redirection to distribute load",
                expected_improvement=15.0,
                gates_to_open=0
            ))
            
        elif pred.risk_level == RiskLevel.HIGH:
            security_to_open = min(5, max_security - current_security)
            if security_to_open > 0:
                recs.append(Recommendation(
                    action=ActionType.OPEN_SECURITY,
                    priority="high",
                    description=f"⚠️ Open {security_to_open} security lanes to reduce wait times",
                    expected_improvement=18.0,
                    gates_to_open=security_to_open
                ))
                
        elif pred.risk_level == RiskLevel.MODERATE:
            security_to_open = min(3, max_security - current_security)
            if security_to_open > 0:
                recs.append(Recommendation(
                    action=ActionType.OPEN_SECURITY,
                    priority="medium",
                    description=f"📊 Consider opening {security_to_open} security lanes",
                    expected_improvement=10.0,
                    gates_to_open=security_to_open
                ))
        
        return recs
    
    def _exit_recommendations(
        self, pred: Prediction, resources: Dict
    ) -> List[Recommendation]:
        """Generate exit-specific recommendations."""
        recs = []
        
        current_exits = resources.get('active_exit_gates', 25)
        max_exits = resources.get('max_exit_gates', 60)
        
        if pred.risk_level == RiskLevel.CRITICAL:
            exits_to_open = min(15, max_exits - current_exits)
            if exits_to_open > 0:
                recs.append(Recommendation(
                    action=ActionType.OPEN_EXIT,
                    priority="urgent",
                    description=f"🚨 CRITICAL: Open {exits_to_open} exit gates NOW",
                    expected_improvement=30.0,
                    gates_to_open=exits_to_open
                ))
            
            recs.append(Recommendation(
                action=ActionType.ENABLE_REDIRECT,
                priority="urgent",
                description="🚨 Redirect fans to less crowded exits",
                expected_improvement=20.0,
                gates_to_open=0
            ))
            
        elif pred.risk_level == RiskLevel.HIGH:
            exits_to_open = min(10, max_exits - current_exits)
            if exits_to_open > 0:
                recs.append(Recommendation(
                    action=ActionType.OPEN_EXIT,
                    priority="high",
                    description=f"⚠️ Open {exits_to_open} exit gates to ease congestion",
                    expected_improvement=22.0,
                    gates_to_open=exits_to_open
                ))
                
        elif pred.risk_level == RiskLevel.MODERATE:
            exits_to_open = min(5, max_exits - current_exits)
            if exits_to_open > 0:
                recs.append(Recommendation(
                    action=ActionType.OPEN_EXIT,
                    priority="medium",
                    description=f"📊 Prepare {exits_to_open} additional exit gates",
                    expected_improvement=12.0,
                    gates_to_open=exits_to_open
                ))
        
        return recs
    
    def get_status_summary(self, entry_pred: Prediction, exit_pred: Prediction) -> Dict:
        """Get a summary of current status for display."""
        # Determine overall status
        max_risk = max(entry_pred.risk_score, exit_pred.risk_score)
        
        if max_risk >= 0.75:
            overall_status = "CRITICAL"
            status_color = "#dc2626"
            status_icon = "🚨"
        elif max_risk >= 0.55:
            overall_status = "WARNING"
            status_color = "#f59e0b"
            status_icon = "⚠️"
        elif max_risk >= 0.35:
            overall_status = "ELEVATED"
            status_color = "#3b82f6"
            status_icon = "📊"
        else:
            overall_status = "NORMAL"
            status_color = "#10b981"
            status_icon = "✅"
        
        primary_concern = "EXIT" if exit_pred.risk_score > entry_pred.risk_score else "ENTRY"
        
        return {
            'overall_status': overall_status,
            'status_color': status_color,
            'status_icon': status_icon,
            'primary_concern': primary_concern,
            'entry_risk': entry_pred.risk_score,
            'exit_risk': exit_pred.risk_score,
            'entry_level': entry_pred.risk_level.value,
            'exit_level': exit_pred.risk_level.value
        }


# Singleton instance for easy import
_predictor_instance: Optional[StadiumRiskPredictor] = None


def get_predictor(kickoff_time: int = 180) -> StadiumRiskPredictor:
    """Get or create the global predictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = StadiumRiskPredictor(kickoff_time)
    return _predictor_instance
