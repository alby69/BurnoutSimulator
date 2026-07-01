from fastapi import FastAPI, WebSocket, HTTPException
from simulation.world import World
from typing import List, Optional
import asyncio
from pydantic import BaseModel

app = FastAPI(title="Burnout Simulator - Social Lab API")

world = World()

class ControlAction(BaseModel):
    action: str # play, pause, step, speed
    value: Optional[str] = None

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.websocket("/ws/simulation")
async def simulation_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            snapshot = world.get_current_snapshot()
            await websocket.send_json(snapshot.model_dump(mode='json'))
            await asyncio.sleep(world.tick_interval)
    except Exception as e:
        print(f"WS Disconnected: {e}")

@app.post("/api/simulation/control")
async def control_simulation(action: ControlAction):
    if action.action == "play":
        # logic to start simulation
        return {"message": "Simulation started"}
    elif action.action == "pause":
        return {"message": "Simulation paused"}
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

@app.get("/api/agents")
async def list_agents():
    return [{"id": aid, "type": "ai"} for aid in world.agents]
