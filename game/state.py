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
inspected_agent_id: Optional[str] = None
stats_before: Dict = {}
choice_history: List = []
_tutorial_active: bool = False
_tutorial_step: int = 0
_timer_active: bool = False
_decision_start: float = 0.0
_layout_mode: str = "desktop"
_skip_tutorial: bool = False
_high_contrast: bool = False
_reading_speed: float = 0.015  # Seconds per character (~15ms, 200 chars in 3s)

# Initialize swarm once
swarm.load_swarm(force_reinit=True)
