import pytest
import asyncio
from engine.psych_engine import PsychologicalProfile, PsychometricEngine
from agents.archetypes import NaiveOptimist, CynicalSurvivor

def test_psych_engine_evaluation():
    engine = PsychometricEngine()
    profile = PsychologicalProfile(current_stress=10)
    choice = {
        "tags": ["yes_man"],
        "effects": {"stress": 5}
    }
    updated_profile = engine.evaluate_choice(profile, choice, {})

    assert updated_profile.current_stress == 15
    assert updated_profile.agreeableness > 50

@pytest.mark.asyncio
async def test_agent_decision():
    agent = NaiveOptimist()
    # Ensure agreeableness is high for the test
    agent.profile.agreeableness = 90
    choices = [
        {"id": "stressful", "effects": {"stress": 20}},
        {"id": "calm", "effects": {"stress": 0}}
    ]
    # NaiveOptimist is highly agreeable, should pick the calm choice
    decision = await agent.decide(choices)
    assert decision["id"] == "calm"

@pytest.mark.asyncio
async def test_agent_learning():
    agent = CynicalSurvivor()
    outcome = {
        "choice": {"tags": ["survivor"], "effects": {"stress": 10}},
        "context": {}
    }
    old_stress = agent.profile.current_stress
    await agent.learn(outcome)
    assert agent.profile.current_stress > old_stress
    assert agent.profile.resilience > 50
