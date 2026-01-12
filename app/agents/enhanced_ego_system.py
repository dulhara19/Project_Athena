"""
Enhanced ego system - unified interface for all ego components.
Integrates all ego-related functionality into a single system.
"""
from typing import Dict, Any, Optional
from app.agents.ego_structure import EgoDimensions
from app.agents.ego_impact import EgoImpactCalculator
from app.agents.ego_evolution import EgoEvolution
from app.agents.ego_defense import EgoDefenseMechanisms
from app.agents.hybrid_ego_pain import HybridEgoPainCalculator
from app.agents.ego_metrics import EgoMetrics
from app.config import config
from app.utils.logger import logger
from app.utils.error_handler import EgoCalculationError, handle_error


class EnhancedEgoSystem:
    """
    Complete enhanced ego system.
    Provides unified interface for all ego operations.
    """
    
    def __init__(self, initial_ego_strength: Optional[float] = None):
        """
        Initialize enhanced ego system.
        
        Args:
            initial_ego_strength: Optional initial ego strength
        """
        # Initialize core components
        self.ego_dimensions = EgoDimensions(initial_strength=initial_ego_strength)
        self.ego_evolution = EgoEvolution(self.ego_dimensions)
        self.ego_defense = EgoDefenseMechanisms(self.ego_dimensions)
        self.pain_calculator = HybridEgoPainCalculator()
        self.metrics = EgoMetrics(
            self.ego_dimensions, 
            self.ego_evolution, 
            self.ego_defense
        )
        
        logger.info("EnhancedEgoSystem initialized")
    
    def process_user_input(
        self, 
        user_input: str,
        use_llm: bool = True,
        apply_defense: bool = True
    ) -> Dict[str, Any]:
        """
        Main entry point for ego processing.
        
        Args:
            user_input: User's input text
            use_llm: Whether to use LLM in pain calculation
            apply_defense: Whether to apply defense mechanisms
            
        Returns:
            Complete ego analysis dictionary
        """
        try:
            # Step 1: Calculate pain using hybrid approach
            pain_analysis = self.pain_calculator.calculate_pain(
                user_input, 
                self.ego_dimensions,
                use_llm=use_llm
            )
            
            # Step 2: Apply defense mechanisms if needed
            defense_result = None
            final_pain = pain_analysis["final_pain"]
            
            if apply_defense:
                defense_result = self.ego_defense.apply_defense(
                    pain_analysis["final_pain"],
                    pain_analysis["most_affected_dimension"]
                )
                
                if defense_result["defense_applied"]:
                    final_pain = defense_result["modified_pain"]
            
            # Step 3: Update ego based on interaction
            self.ego_evolution.update_ego_from_interaction(
                user_input,
                pain_analysis["dimension_impacts"]
            )
            
            # Step 4: Get metrics
            metrics = self.metrics.get_comprehensive_metrics()
            
            # Compile complete result
            result = {
                "pain_analysis": pain_analysis,
                "defense_result": defense_result,
                "final_pain": final_pain,
                "ego_metrics": metrics,
                "ego_state": {
                    "strength": self.ego_dimensions.ego_strength,
                    "fragility": self.ego_dimensions.ego_fragility,
                    "consistency": self.ego_evolution.get_ego_consistency_score(),
                    "evolution_trend": self.ego_evolution.get_evolution_trend(),
                    "dimensions": {
                        k: dict(v) 
                        for k, v in self.ego_dimensions.dimensions.items()
                    }
                }
            }
            
            logger.debug(f"Processed user input: final_pain={final_pain:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing user input in ego system: {e}")
            handle_error(e, {"function": "process_user_input", "user_input": user_input[:50]})
            raise EgoCalculationError(f"Failed to process ego: {e}")
    
    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current ego state without processing new input.
        
        Returns:
            Current ego state dictionary
        """
        return {
            "ego_strength": self.ego_dimensions.ego_strength,
            "ego_fragility": self.ego_dimensions.ego_fragility,
            "dimensions": {
                k: dict(v) 
                for k, v in self.ego_dimensions.dimensions.items()
            },
            "metrics": self.metrics.get_comprehensive_metrics()
        }
    
    def reset_ego(self, new_strength: Optional[float] = None):
        """
        Reset ego to initial state.
        
        Args:
            new_strength: Optional new ego strength
        """
        self.ego_dimensions = EgoDimensions(initial_strength=new_strength)
        self.ego_evolution = EgoEvolution(self.ego_dimensions)
        self.ego_defense = EgoDefenseMechanisms(self.ego_dimensions)
        self.metrics = EgoMetrics(
            self.ego_dimensions, 
            self.ego_evolution, 
            self.ego_defense
        )
        logger.info("Ego system reset")
    
    def export_for_research(self) -> Dict[str, Any]:
        """
        Export complete ego system state for research analysis.
        
        Returns:
            Research-ready export dictionary
        """
        return {
            "ego_system": self.get_current_state(),
            "research_metrics": self.metrics.get_research_summary(),
            "evolution_history": {
                "interactions": len(self.ego_evolution.interaction_history),
                "snapshots": len(self.ego_evolution.ego_snapshot_history),
                "recent_snapshots": self.ego_evolution.ego_snapshot_history[-10:] if len(self.ego_evolution.ego_snapshot_history) > 0 else []
            },
            "defense_history": self.ego_defense.defense_activation_history[-20:] if self.ego_defense.defense_activation_history else []
        }

