"""
Pydantic schemas for API request/response models.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class UserInputRequest(BaseModel):
    """Request model for user input."""
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    text: str = Field(..., min_length=1, description="User input text")


class WorkflowStep(BaseModel):
    """Single workflow step information."""
    step_number: int
    step_name: str
    status: str = Field(..., description="pending, processing, completed, error")
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class WorkflowProgress(BaseModel):
    """Workflow progress update."""
    workflow_id: str
    current_step: int
    total_steps: int
    steps: List[WorkflowStep]
    progress_percentage: float


class InteractionResponse(BaseModel):
    """Complete interaction response."""
    user_id: str
    session_id: str
    user_input: str
    athena_response: str
    workflow_steps: List[WorkflowStep]
    metrics: Dict[str, Any]
    ego_state: Dict[str, Any]
    empathy_metrics: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)


class MetricsResponse(BaseModel):
    """Metrics response."""
    ego_metrics: Dict[str, Any]
    empathy_metrics: Optional[Dict[str, Any]] = None
    interaction_count: int
    session_duration: Optional[float] = None


class EgoStateResponse(BaseModel):
    """Ego state response."""
    ego_strength: float
    ego_fragility: float
    consistency: float
    evolution_trend: str
    dimensions: Dict[str, Dict[str, float]]
    defense_stats: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Error response."""
    error: bool = True
    error_type: str
    error_message: str
    context: Optional[Dict[str, Any]] = None

