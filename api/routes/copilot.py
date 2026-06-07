from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from core.groq_client import GroqClient
from pydantic import BaseModel

router = APIRouter()
groq = GroqClient()

COPILOT_SYSTEM = """
You are an AI Ops Copilot for a Splunk observability platform.
Answer questions about incidents, logs, and system health.
Be concise, technical, and actionable.
"""

class CopilotRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_copilot(req: CopilotRequest):
    async def stream():
        async for chunk in groq.stream_reason(COPILOT_SYSTEM, req.question):
            yield chunk
    return StreamingResponse(stream(), media_type="text/plain")
