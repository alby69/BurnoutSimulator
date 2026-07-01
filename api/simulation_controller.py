from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class SimulationStatus(BaseModel):
    is_running: bool
    current_tick: int

@router.get("/status")
async def get_status():
    return {"is_running": False, "current_tick": 0}
