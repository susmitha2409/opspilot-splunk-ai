from fastapi import APIRouter
from agents.orchestrator import AgentOrchestrator
from memory.memory_manager import MemoryManager
from pydantic import BaseModel

router = APIRouter()
orch = AgentOrchestrator()

class InvestigationRequest(BaseModel):
    service:  str
    severity: str = "HIGH"
    message:  str = ""

@router.post("/investigate")
async def investigate(req: InvestigationRequest):
    result = await orch.investigate(req.dict())
    return {"status": "complete", "report": result}

@router.get("/history")
async def history():
    mem = MemoryManager()
    return {"incidents": await mem.get_recent(10)}
