from fastapi import FastAPI
from app.routes import chat

app = FastAPI(title="Self-Aware AI Mentor")

app.include_router(chat.router, prefix="/api", tags=["Chat"])

@app.get("/")
def root():
    return {"message": "Self-Aware AI Mentor is running"}
