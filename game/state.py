from typing import Optional, Dict, List
from game.engine import GameEngine
from agents.swarm import AgentSwarm

# ── Global State ──
screen: str = "start"
engine: Optional[GameEngine] = None
session_id: Optional[str] = None
swarm: AgentSwarm = AgentSwarm(num_agents=6)
current_human_id: Optional[str] = None
current_agent_id: Optional[str] = None
client_inspected_agent: Dict[str, str] = {}
stats_before: Dict = {}
choice_history: List = []
_tutorial_active: bool = False
_tutorial_step: int = 0
_timer_active: bool = False
_decision_start: float = 0.0
_layout_mode: str = "desktop"
_skip_tutorial: bool = False

# Initialize swarm once
swarm.load_swarm()
