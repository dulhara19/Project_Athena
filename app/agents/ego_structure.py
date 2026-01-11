"""
Multi-dimensional ego structure for Athena.
Novel contribution: First computational model of ego with 6 measurable dimensions.
"""
from typing import Dict, Any, List
from app.config import config
from app.utils.logger import logger


class EgoDimensions:
    """
    Multi-dimensional ego model based on psychological research.
    
    Dimensions:
    1. Identity - Self-concept, self-esteem, authenticity
    2. Competence - Intelligence perception, capability confidence, achievement pride
    3. Social - Belonging need, recognition need, love need
    4. Values - Value integrity, moral standing, purpose alignment
    5. Relationships - Attachment security, trust level, intimacy comfort
    6. Interests - Interest validation, hobby importance, passion intensity
    """
    
    def __init__(self, initial_strength: float = None):
        """
        Initialize ego dimensions with default values.
        
        Args:
            initial_strength: Initial ego strength (0-1), defaults to config value
        """
        self.dimensions = {
            "identity": {
                "self_esteem": 0.8,  # How much agent values itself
                "self_concept_clarity": 0.7,  # How clear agent's self-image is
                "authenticity": 0.9  # How true to self agent feels
            },
            "competence": {
                "intelligence_self_perception": 0.8,
                "capability_confidence": 0.7,
                "achievement_pride": 0.6
            },
            "social": {
                "belonging_need": 0.8,  # Need to be accepted
                "recognition_need": 0.7,  # Need to be acknowledged
                "love_need": 0.9  # Need to be loved/cared for
            },
            "values": {
                "value_integrity": 0.9,  # How much values are threatened
                "moral_standing": 0.8,
                "purpose_alignment": 0.7
            },
            "relationships": {
                "attachment_security": 0.8,
                "trust_level": 0.7,
                "intimacy_comfort": 0.6
            },
            "interests": {
                "interest_validation": 0.7,  # How much interests matter
                "hobby_importance": 0.6,
                "passion_intensity": 0.8
            }
        }
        
        # Ego strength (overall resilience)
        self.ego_strength = initial_strength or config.EGO_STRENGTH_DEFAULT
        self.ego_fragility = 1.0 - self.ego_strength
        
        # Vulnerability weights (which dimensions are most sensitive)
        # Higher weight = more impact on overall ego
        self.vulnerability_weights = {
            "identity": 0.25,  # Most important
            "social": 0.20,
            "values": 0.20,
            "competence": 0.15,
            "relationships": 0.15,
            "interests": 0.05  # Least important
        }
        
        logger.debug(f"Initialized EgoDimensions with strength {self.ego_strength}")
    
    def get_dimension_value(self, dimension: str, sub_dimension: str = None) -> float:
        """
        Get value for a dimension or sub-dimension.
        
        Args:
            dimension: Dimension name
            sub_dimension: Optional sub-dimension name
            
        Returns:
            Value (0-1) or average if sub_dimension not specified
        """
        if dimension not in self.dimensions:
            logger.warning(f"Unknown dimension: {dimension}")
            return 0.5
        
        dim_dict = self.dimensions[dimension]
        
        if sub_dimension:
            return dim_dict.get(sub_dimension, 0.5)
        else:
            # Return average of all sub-dimensions
            return sum(dim_dict.values()) / len(dim_dict)
    
    def update_dimension(self, dimension: str, sub_dimension: str, value: float):
        """
        Update a specific sub-dimension value.
        
        Args:
            dimension: Dimension name
            sub_dimension: Sub-dimension name
            value: New value (will be clamped to 0-1)
        """
        if dimension not in self.dimensions:
            logger.warning(f"Unknown dimension: {dimension}")
            return
        
        if sub_dimension not in self.dimensions[dimension]:
            logger.warning(f"Unknown sub-dimension: {sub_dimension} in {dimension}")
            return
        
        # Clamp value to [0, 1]
        value = max(0.0, min(1.0, float(value)))
        self.dimensions[dimension][sub_dimension] = value
        logger.debug(f"Updated {dimension}.{sub_dimension} = {value}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ego dimensions to dictionary for serialization.
        
        Returns:
            Dictionary representation
        """
        return {
            "dimensions": {k: dict(v) for k, v in self.dimensions.items()},
            "ego_strength": self.ego_strength,
            "ego_fragility": self.ego_fragility,
            "vulnerability_weights": self.vulnerability_weights.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EgoDimensions':
        """
        Create EgoDimensions from dictionary.
        
        Args:
            data: Dictionary with dimensions data
            
        Returns:
            EgoDimensions instance
        """
        instance = cls(initial_strength=data.get("ego_strength", config.EGO_STRENGTH_DEFAULT))
        
        if "dimensions" in data:
            for dim_name, dim_data in data["dimensions"].items():
                if dim_name in instance.dimensions:
                    instance.dimensions[dim_name].update(dim_data)
        
        if "vulnerability_weights" in data:
            instance.vulnerability_weights.update(data["vulnerability_weights"])
        
        return instance

