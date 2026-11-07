from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional

from app.database.connection import get_db
from app.core.security import get_current_user_id
from app.services.llm_service import LLMService

router = APIRouter()


class ChatMessage(BaseModel):
    role: str    # "user" | "bot"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    reply: str


class VoiceRequest(BaseModel):
    audio: str        # base64 encoded audio
    language: str = "en"


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Send a message to the AI health chatbot."""
    llm = LLMService()
    history = [{"role": m.role, "content": m.content} for m in (payload.history or [])]
    reply = await llm.chat(payload.message, history)
    return {"reply": reply}


@router.post("/voice")
async def voice_chat(
    payload: VoiceRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Process voice input and return text + audio reply."""
    from app.services.speech_service import SpeechService
    speech = SpeechService()
    transcript = await speech.transcribe(payload.audio, payload.language)

    llm = LLMService()
    reply_text = await llm.chat(transcript, [])

    audio_reply = await speech.synthesize(reply_text, payload.language)
    return {"text": transcript, "reply": reply_text, "audioReply": audio_reply}


@router.get("/history")
async def get_history(user_id: str = Depends(get_current_user_id)):
    """Return chat history (in-memory stub; replace with DB persistence if needed)."""
    return {"history": []}


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_history(user_id: str = Depends(get_current_user_id)):
    """Clear chat history for the current user."""
    return None
