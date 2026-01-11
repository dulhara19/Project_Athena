"""
Ego evolution tracking system - monitors how ego changes over time.
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
from app.agents.ego_structure import EgoDimensions
from app.config import config
from app.utils.logger import logger


class EgoEvolution:
    """
    Tracks and evolves ego based on interaction history.
    Provides consistency metrics and evolution trends.
    """
    
    def __init__(self, ego_dimensions: EgoDimensions):
        """
        Initialize ego evolution tracker.
        
        Args:
            ego_dimensions: EgoDimensions instance to track
        """
        self.ego_dimensions = ego_dimensions
        self.interaction_history: List[Dict] = []
        self.ego_snapshot_history: List[Dict] = []
        self.learning_rate = config.EGO_LEARNING_RATE
        
        logger.debug("EgoEvolution initialized")
    
    def update_ego_from_interaction(
        self, 
        user_input: str,
        impact_scores: Dict[str, float],
        learning_rate: Optional[float] = None
    ):
        """
        Gradually update ego dimensions based on repeated patterns.
        
        Args:
            user_input: User's input text
            impact_scores: Dictionary of dimension -> impact score
            learning_rate: Optional learning rate override
        """
        lr = learning_rate or self.learning_rate
        
        # Store interaction
        self.interaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "impacts": impact_scores.copy()
        })
        
        # Update dimensions based on cumulative impact
        for dimension, impact in impact_scores.items():
            if dimension in self.ego_dimensions.dimensions:
                # Get current value
                dim_dict = self.ego_dimensions.dimensions[dimension]
                
                # Update each sub-dimension proportionally
                for sub_dim in dim_dict:
                    current_val = dim_dict[sub_dim]
                    
                    # If positive impact, increase confidence
                    if impact > 0.1:
                        new_val = current_val + (impact * lr)
                        dim_dict[sub_dim] = min(1.0, new_val)
                    
                    # If negative impact, decrease confidence
                    elif impact < -0.1:
                        new_val = current_val + (impact * lr)
                        dim_dict[sub_dim] = max(0.0, new_val)
        
        # Update ego strength based on consistency
        self._update_ego_strength()
        
        # Save snapshot
        self._save_ego_snapshot()
        
        logger.debug(f"Updated ego from interaction (learning_rate={lr})")
    
    def _update_ego_strength(self):
        """
        Ego strength increases with consistency, decreases with volatility.
        """
        if len(self.interaction_history) < 5:
            return
        
        # Calculate volatility (how much impacts vary)
        recent_impacts = [h["impacts"] for h in self.interaction_history[-10:]]
        
        # Average absolute impact per dimension
        avg_abs_impacts = {}
        for dim in recent_impacts[0].keys():
            abs_vals = [abs(imp.get(dim, 0)) for imp in recent_impacts if dim in imp]
            if abs_vals:
                avg_abs_impacts[dim] = sum(abs_vals) / len(abs_vals)
            else:
                avg_abs_impacts[dim] = 0.0
        
        # High volatility = lower strength
        total_volatility = sum(avg_abs_impacts.values()) / len(avg_abs_impacts) if avg_abs_impacts else 0.0
        volatility_factor = min(1.0, total_volatility)
        
        # Strength inversely related to volatility
        # High volatility (1.0) reduces strength by 50%
        new_strength = 1.0 - (volatility_factor * 0.5)
        self.ego_dimensions.ego_strength = max(0.3, min(1.0, new_strength))
        self.ego_dimensions.ego_fragility = 1.0 - self.ego_dimensions.ego_strength
        
        logger.debug(f"Updated ego strength: {self.ego_dimensions.ego_strength} (volatility: {volatility_factor})")
    
    def _save_ego_snapshot(self):
        """Save ego state for analysis."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "dimensions": {k: dict(v) for k, v in self.ego_dimensions.dimensions.items()},
            "ego_strength": self.ego_dimensions.ego_strength,
            "ego_fragility": self.ego_dimensions.ego_fragility,
            "interaction_count": len(self.interaction_history)
        }
        self.ego_snapshot_history.append(snapshot)
        
        # Keep only last 100 snapshots
        if len(self.ego_snapshot_history) > 100:
            self.ego_snapshot_history = self.ego_snapshot_history[-100:]
    
    def get_ego_consistency_score(self) -> float:
        """
        Returns 0-1 score of how consistent ego has been.
        Higher = more stable/consistent.
        
        Returns:
            Consistency score (0-1)
        """
        if len(self.ego_snapshot_history) < 2:
            return 1.0
        
        # Calculate variance in ego strength over time
        strengths = [s["ego_strength"] for s in self.ego_snapshot_history]
        if len(strengths) < 2:
            return 1.0
        
        mean_strength = sum(strengths) / len(strengths)
        variance = sum((s - mean_strength) ** 2 for s in strengths) / len(strengths)
        
        # Lower variance = higher consistency
        # Scale variance (max variance for 0-1 range is 0.25, so multiply by 4)
        consistency = 1.0 - min(1.0, variance * 4.0)
        consistency = max(0.0, consistency)
        
        logger.debug(f"Ego consistency score: {consistency} (variance: {variance})")
        return consistency
    
    def get_evolution_trend(self) -> str:
        """
        Determine if ego is strengthening, weakening, or stable.
        
        Returns:
            "strengthening", "weakening", "stable", or "insufficient_data"
        """
        if len(self.ego_snapshot_history) < 5:
            return "insufficient_data"
        
        recent = self.ego_snapshot_history[-5:]
        strengths = [s["ego_strength"] for s in recent]
        
        # Simple linear trend
        if strengths[-1] > strengths[0] + 0.1:
            return "strengthening"
        elif strengths[-1] < strengths[0] - 0.1:
            return "weakening"
        else:
            return "stable"
    
    def get_history_summary(self) -> Dict:
        """
        Get summary of interaction history.
        
        Returns:
            Dictionary with history statistics
        """
        return {
            "total_interactions": len(self.interaction_history),
            "snapshots_count": len(self.ego_snapshot_history),
            "consistency_score": self.get_ego_consistency_score(),
            "evolution_trend": self.get_evolution_trend(),
            "current_strength": self.ego_dimensions.ego_strength
        }

