from fastapi import APIRouter
from app.models.schemas import ChatRequest
from app.services.ai_agent import ask_agent

router = APIRouter()

@router.post("/chat")
async def chat_with_agent(request: ChatRequest):
    response = ask_agent(request.message)
    return {"reply": response}
