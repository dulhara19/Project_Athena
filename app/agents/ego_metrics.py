"""
Ego metrics framework for research.
Provides comprehensive metrics for analyzing ego system performance.
"""
from typing import Dict, Any
from app.agents.ego_structure import EgoDimensions
from app.agents.ego_evolution import EgoEvolution
from app.agents.ego_defense import EgoDefenseMechanisms
from app.utils.logger import logger


class EgoMetrics:
    """
    Research metrics for ego system.
    Provides quantifiable metrics for publication and analysis.
    """
    
    def __init__(
        self, 
        ego_dimensions: EgoDimensions, 
        ego_evolution: EgoEvolution,
        ego_defense: EgoDefenseMechanisms = None
    ):
        """
        Initialize metrics framework.
        
        Args:
            ego_dimensions: EgoDimensions instance
            ego_evolution: EgoEvolution instance
            ego_defense: Optional EgoDefenseMechanisms instance
        """
        self.ego_dimensions = ego_dimensions
        self.ego_evolution = ego_evolution
        self.ego_defense = ego_defense
        logger.debug("EgoMetrics initialized")
    
    def get_comprehensive_metrics(self) -> Dict[str, Any]:
        """
        Get all research metrics.
        
        Returns:
            Dictionary with comprehensive metrics
        """
        return {
            "ego_strength": self.ego_dimensions.ego_strength,
            "ego_fragility": self.ego_dimensions.ego_fragility,
            "ego_consistency": self.ego_evolution.get_ego_consistency_score(),
            "dimension_health": self._calculate_dimension_health(),
            "vulnerability_profile": self.ego_dimensions.vulnerability_weights.copy(),
            "evolution_trend": self.ego_evolution.get_evolution_trend(),
            "defense_mechanism_usage": self._get_defense_stats(),
            "interaction_count": len(self.ego_evolution.interaction_history),
            "snapshot_count": len(self.ego_evolution.ego_snapshot_history),
            "dimension_values": self._get_dimension_values()
        }
    
    def _calculate_dimension_health(self) -> Dict[str, float]:
        """
        Calculate health score for each dimension (0-1).
        Higher = healthier/more stable.
        
        Returns:
            Dictionary mapping dimension names to health scores
        """
        health_scores = {}
        for dimension, sub_dims in self.ego_dimensions.dimensions.items():
            # Average of sub-dimension values
            avg_value = sum(sub_dims.values()) / len(sub_dims)
            health_scores[dimension] = avg_value
        
        return health_scores
    
    def _get_dimension_values(self) -> Dict[str, Dict[str, float]]:
        """
        Get current values for all dimensions and sub-dimensions.
        
        Returns:
            Nested dictionary of dimension -> sub_dimension -> value
        """
        return {
            dim: dict(sub_dims) 
            for dim, sub_dims in self.ego_dimensions.dimensions.items()
        }
    
    def _get_defense_stats(self) -> Dict[str, Any]:
        """
        Get defense mechanism statistics.
        
        Returns:
            Dictionary with defense statistics
        """
        if self.ego_defense:
            return self.ego_defense.get_defense_stats()
        else:
            return {
                "total_defenses": 0,
                "by_type": {},
                "average_reduction": 0.0
            }
    
    def get_research_summary(self) -> Dict[str, Any]:
        """
        Get summary suitable for research publication.
        
        Returns:
            Dictionary with research-ready summary
        """
        metrics = self.get_comprehensive_metrics()
        
        return {
            "ego_system_summary": {
                "strength": round(metrics["ego_strength"], 3),
                "consistency": round(metrics["ego_consistency"], 3),
                "trend": metrics["evolution_trend"],
                "fragility": round(metrics["ego_fragility"], 3)
            },
            "dimension_analysis": {
                "health_scores": {
                    k: round(v, 3) 
                    for k, v in metrics["dimension_health"].items()
                },
                "vulnerability_weights": metrics["vulnerability_profile"]
            },
            "interaction_analysis": {
                "total_interactions": metrics["interaction_count"],
                "snapshots_recorded": metrics["snapshot_count"],
                "defense_usage": metrics["defense_mechanism_usage"]
            },
            "methodology": {
                "dimensions": 6,
                "sub_dimensions_per_dimension": 3,
                "total_sub_dimensions": 18,
                "defense_levels": 3
            }
        }

