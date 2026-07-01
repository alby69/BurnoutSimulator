from psychology.profile import PsychologicalProfile
from psychology.stress_model import DynamicStressModel
from agents.base_agent import BaseAgent, Situation, Action
from agents.ai_agent import AIAgent
from simulation.world import World, WorldSnapshot
from simulation.clock import Clock
from api.main import app
import pytest

def test_imports():
    profile = PsychologicalProfile(stress_level=0.5)
    model = DynamicStressModel()
    risk = model.calculate_burnout_risk(profile)
    assert risk.risk_score > 0

    world = World()
    snapshot = world.get_current_snapshot()
    assert snapshot is not None

def test_agent_creation():
    profile = PsychologicalProfile()
    agent = AIAgent(agent_id="test_bot", profile=profile, archetype="test", company_role="worker")
    assert agent.agent_id == "test_bot"
    assert agent.profile.stress_level == 0.0

if __name__ == "__main__":
    test_imports()
    test_agent_creation()
    print("Basic tests passed!")
