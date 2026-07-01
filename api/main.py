from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from engine.psych_engine import PsychologicalProfile

app = FastAPI(title="BurnoutSimulator v3.0 API")

class SimulationRequest(BaseModel):
    agent_type: str
    scenario_id: str

@app.get("/")
async def root():
    return {"message": "BurnoutSimulator v3.0 API", "status": "active"}

@app.post("/simulate")
async def run_simulation(request: SimulationRequest):
    # This would trigger an agent-based simulation
    return {
        "status": "success",
        "agent": request.agent_type,
        "result": "burnout_avoided",
        "metrics": {"stress": 45.0, "resilience": 62.0}
    }

@app.get("/profiles/{agent_id}")
async def get_agent_profile(agent_id: str):
    # Placeholder for database retrieval
    return PsychologicalProfile().to_dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
