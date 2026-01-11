"""
Ego defense mechanisms - psychological defense mechanisms for ego protection.
Novel contribution: Computational implementation of defense mechanisms.
"""
from typing import Dict, Any, List
from datetime import datetime
from app.agents.ego_structure import EgoDimensions
from app.utils.logger import logger


class EgoDefenseMechanisms:
    """
    Implements psychological defense mechanisms for ego protection.
    
    Defense levels:
    - Mature: Humor, sublimation, anticipation (healthy, ego strength > 0.7)
    - Neurotic: Rationalization, displacement (moderate, ego strength 0.4-0.7)
    - Primitive: Denial, projection (unhealthy, ego strength < 0.4)
    """
    
    def __init__(self, ego_dimensions: EgoDimensions):
        """
        Initialize defense mechanisms.
        
        Args:
            ego_dimensions: EgoDimensions instance
        """
        self.ego_dimensions = ego_dimensions
        self.defense_activation_history: List[Dict] = []
        logger.debug("EgoDefenseMechanisms initialized")
    
    def apply_defense(
        self, 
        threat_level: float, 
        affected_dimension: str
    ) -> Dict[str, Any]:
        """
        Apply defense mechanisms based on threat level and ego strength.
        
        Args:
            threat_level: Threat level (-1 to +1, negative = threat)
            affected_dimension: Which ego dimension is affected
            
        Returns:
            Dictionary with defense information
        """
        # Only activate if threat is significant
        if abs(threat_level) < 0.3:
            return {
                "defense_applied": False,
                "original_pain": threat_level,
                "modified_pain": threat_level,
                "defense_type": None,
                "defense_description": None
            }
        
        # Select defense mechanism based on ego strength
        ego_strength = self.ego_dimensions.ego_strength
        
        if ego_strength > 0.7:
            # Strong ego: use mature defenses
            defense_type = self._mature_defense(threat_level, affected_dimension)
        elif ego_strength > 0.4:
            # Moderate ego: use neurotic defenses
            defense_type = self._neurotic_defense(threat_level, affected_dimension)
        else:
            # Weak ego: use primitive defenses
            defense_type = self._primitive_defense(threat_level, affected_dimension)
        
        # Calculate pain reduction
        pain_reduction = defense_type["reduction_factor"]
        modified_pain = threat_level * (1.0 - pain_reduction)
        
        # Record defense activation
        self.defense_activation_history.append({
            "timestamp": datetime.now().isoformat(),
            "threat_level": threat_level,
            "affected_dimension": affected_dimension,
            "defense_type": defense_type["name"],
            "pain_reduction": pain_reduction,
            "ego_strength": ego_strength
        })
        
        logger.info(
            f"Defense applied: {defense_type['name']} "
            f"(threat: {threat_level:.2f}, reduction: {pain_reduction:.2f})"
        )
        
        return {
            "defense_applied": True,
            "original_pain": threat_level,
            "modified_pain": modified_pain,
            "defense_type": defense_type["name"],
            "defense_description": defense_type["description"],
            "reduction_factor": pain_reduction,
            "ego_strength": ego_strength
        }
    
    def _mature_defense(self, threat: float, dimension: str) -> Dict:
        """
        Mature defenses: humor, sublimation, anticipation.
        Healthy coping mechanisms.
        """
        defenses = [
            {
                "name": "humor",
                "reduction_factor": 0.3,  # 30% pain reduction
                "description": "Agent uses humor to reframe the threat, finding lightness in the situation"
            },
            {
                "name": "sublimation",
                "reduction_factor": 0.25,
                "description": "Agent channels the threat into productive or creative energy"
            },
            {
                "name": "anticipation",
                "reduction_factor": 0.2,
                "description": "Agent anticipates and prepares for potential threats, reducing impact"
            }
        ]
        
        # Select defense based on dimension (for variety)
        defense_idx = hash(dimension) % len(defenses)
        return defenses[defense_idx]
    
    def _neurotic_defense(self, threat: float, dimension: str) -> Dict:
        """
        Neurotic defenses: rationalization, displacement.
        Moderate coping mechanisms, less healthy.
        """
        defenses = [
            {
                "name": "rationalization",
                "reduction_factor": 0.5,  # 50% pain reduction
                "description": "Agent rationalizes the threat, creating logical explanations to reduce impact"
            },
            {
                "name": "displacement",
                "reduction_factor": 0.45,
                "description": "Agent redirects emotional response to a less threatening target"
            },
            {
                "name": "intellectualization",
                "reduction_factor": 0.4,
                "description": "Agent focuses on intellectual aspects, avoiding emotional impact"
            }
        ]
        
        defense_idx = hash(dimension) % len(defenses)
        return defenses[defense_idx]
    
    def _primitive_defense(self, threat: float, dimension: str) -> Dict:
        """
        Primitive defenses: denial, projection.
        Unhealthy but effective at reducing immediate pain.
        """
        defenses = [
            {
                "name": "denial",
                "reduction_factor": 0.7,  # 70% pain reduction (but unhealthy)
                "description": "Agent denies the threat exists, refusing to acknowledge it"
            },
            {
                "name": "projection",
                "reduction_factor": 0.65,
                "description": "Agent projects the threat onto others, avoiding self-blame"
            },
            {
                "name": "repression",
                "reduction_factor": 0.6,
                "description": "Agent represses awareness of the threat, pushing it out of consciousness"
            }
        ]
        
        defense_idx = hash(dimension) % len(defenses)
        return defenses[defense_idx]
    
    def get_defense_stats(self) -> Dict[str, Any]:
        """
        Get statistics about defense mechanism usage.
        
        Returns:
            Dictionary with defense statistics
        """
        if not self.defense_activation_history:
            return {
                "total_defenses": 0,
                "by_type": {},
                "average_reduction": 0.0
            }
        
        by_type = {}
        total_reduction = 0.0
        
        for entry in self.defense_activation_history:
            defense_type = entry["defense_type"]
            if defense_type not in by_type:
                by_type[defense_type] = 0
            by_type[defense_type] += 1
            total_reduction += entry["pain_reduction"]
        
        return {
            "total_defenses": len(self.defense_activation_history),
            "by_type": by_type,
            "average_reduction": total_reduction / len(self.defense_activation_history) if self.defense_activation_history else 0.0
        }

