"""
Metrics API routes.
"""
from fastapi import APIRouter, HTTPException
from app.api.schemas import MetricsResponse, ErrorResponse
from app.api.workflow import orchestrator
from app.utils.logger import logger
from app.utils.error_handler import handle_error

router = APIRouter()


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Get current system metrics.
    """
    try:
        ego_state = orchestrator.ego_system.get_current_state()
        metrics = orchestrator.ego_system.metrics.get_comprehensive_metrics()
        
        return MetricsResponse(
            ego_metrics=metrics,
            interaction_count=len(orchestrator.ego_system.ego_evolution.interaction_history),
            session_duration=None
        )
        
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        error_info = handle_error(e, {"endpoint": "/metrics"})
        raise HTTPException(status_code=500, detail=error_info)


@router.get("/metrics/research")
async def get_research_metrics():
    """
    Get research-ready metrics export.
    """
    try:
        return orchestrator.ego_system.export_for_research()
        
    except Exception as e:
        logger.error(f"Research metrics error: {e}")
        error_info = handle_error(e, {"endpoint": "/metrics/research"})
        raise HTTPException(status_code=500, detail=error_info)

