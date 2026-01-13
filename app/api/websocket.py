"""
WebSocket server for real-time workflow updates.
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Callable, Any
import json
from app.utils.logger import logger


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: List[WebSocket] = []
        self.workflow_connections: Dict[str, WebSocket] = {}  # workflow_id -> websocket
    
    async def connect(self, websocket: WebSocket, workflow_id: str = None):
        """
        Accept new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            workflow_id: Optional workflow ID to associate with connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        
        if workflow_id:
            self.workflow_connections[workflow_id] = websocket
        
        logger.info(f"WebSocket connected (total: {len(self.active_connections)})")
    
    def disconnect(self, websocket: WebSocket, workflow_id: str = None):
        """
        Remove WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            workflow_id: Optional workflow ID
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if workflow_id and workflow_id in self.workflow_connections:
            del self.workflow_connections[workflow_id]
        
        logger.info(f"WebSocket disconnected (remaining: {len(self.active_connections)})")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """
        Send message to specific WebSocket.
        
        Args:
            message: Message dictionary
            websocket: Target WebSocket
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {e}")
    
    async def send_to_workflow(self, workflow_id: str, message: Dict[str, Any]):
        """
        Send message to workflow-specific connection.
        
        Args:
            workflow_id: Workflow ID
            message: Message dictionary
        """
        if workflow_id in self.workflow_connections:
            await self.send_personal_message(
                message, 
                self.workflow_connections[workflow_id]
            )
    
    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast message to all connected clients.
        
        Args:
            message: Message dictionary
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to broadcast to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)


# Global connection manager
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, workflow_id: str = None):
    """
    WebSocket endpoint handler.
    
    Args:
        websocket: WebSocket connection
        workflow_id: Optional workflow ID
    """
    await manager.connect(websocket, workflow_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket, workflow_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, workflow_id)

