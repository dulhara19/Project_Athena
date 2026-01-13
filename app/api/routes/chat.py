"""
Chat API routes.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from app.api.schemas import UserInputRequest, InteractionResponse, ErrorResponse
from app.api.workflow import orchestrator
from app.api.websocket import manager, websocket_endpoint
from app.utils.logger import logger
from app.utils.error_handler import handle_error

router = APIRouter()


@router.post("/chat", response_model=InteractionResponse)
async def process_chat(request: UserInputRequest):
    """
    Process user chat input and return response.
    """
    try:
        result = await orchestrator.process_user_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            user_input=request.text
        )
        
        return InteractionResponse(**result)
        
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        error_info = handle_error(e, {"endpoint": "/chat", "user_id": request.user_id})
        raise HTTPException(status_code=500, detail=error_info)


@router.websocket("/ws/{workflow_id}")
async def websocket_route(websocket: WebSocket, workflow_id: str):
    """
    WebSocket endpoint for real-time workflow updates.
    """
    from app.api.websocket import websocket_endpoint
    await websocket_endpoint(websocket, workflow_id)


@router.post("/chat/stream")
async def process_chat_stream(request: UserInputRequest):
    """
    Process chat with WebSocket streaming.
    Returns workflow ID for client to connect via WebSocket.
    """
    import uuid
    workflow_id = str(uuid.uuid4())
    
    # Start workflow in background
    import asyncio
    asyncio.create_task(
        orchestrator.process_user_interaction(
            user_id=request.user_id,
            session_id=request.session_id,
            user_input=request.text,
            workflow_id=workflow_id
        )
    )
    
    return {
        "workflow_id": workflow_id,
        "websocket_url": f"/api/v1/ws/{workflow_id}",
        "status": "started"
    }

