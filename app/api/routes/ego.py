"""
Ego system API routes.
"""
from fastapi import APIRouter, HTTPException
from app.api.schemas import EgoStateResponse, ErrorResponse
from app.api.workflow import orchestrator
from app.utils.logger import logger
from app.utils.error_handler import handle_error

router = APIRouter()


@router.get("/ego/state", response_model=EgoStateResponse)
async def get_ego_state():
    """
    Get current ego state.
    """
    try:
        ego_state = orchestrator.ego_system.get_current_state()
        metrics = orchestrator.ego_system.metrics.get_comprehensive_metrics()
        defense_stats = orchestrator.ego_system.ego_defense.get_defense_stats()
        
        return EgoStateResponse(
            ego_strength=ego_state["ego_strength"],
            ego_fragility=ego_state["ego_fragility"],
            consistency=metrics["ego_consistency"],
            evolution_trend=metrics["evolution_trend"],
            dimensions=ego_state["dimensions"],
            defense_stats=defense_stats
        )
        
    except Exception as e:
        logger.error(f"Ego state error: {e}")
        error_info = handle_error(e, {"endpoint": "/ego/state"})
        raise HTTPException(status_code=500, detail=error_info)


@router.post("/ego/reset")
async def reset_ego(initial_strength: float = None):
    """
    Reset ego system to initial state.
    """
    try:
        orchestrator.ego_system.reset_ego(new_strength=initial_strength)
        return {"status": "reset", "message": "Ego system reset successfully"}
        
    except Exception as e:
        logger.error(f"Ego reset error: {e}")
        error_info = handle_error(e, {"endpoint": "/ego/reset"})
        raise HTTPException(status_code=500, detail=error_info)

