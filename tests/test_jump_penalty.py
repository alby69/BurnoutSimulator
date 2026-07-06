import pytest
from agents.agent import Agent
from agents.personality import AGENT_PROFILES
from game.models import CompanyArchetype

def test_jump_penalty():
    # Setup agent
    profile = AGENT_PROFILES["il_performante"]
    agent = Agent(
        agent_id="test_agent",
        name="Test Agent",
        profile=profile,
        company_type=CompanyArchetype.CORPORATE.value
    )
    agent.initialize_game()

    # Record initial stats
    initial_stress = agent.engine.player.stress
    initial_self_esteem = agent.engine.player.self_esteem
    initial_elena_trust = agent.engine.player.npcs["Elena"].trust

    # Possess and release
    agent.possess("human_1")
    assert agent.is_possessed is True

    agent.release("human_1")
    assert agent.is_possessed is False

    # Verify penalties (taking into account psych profile modulation)
    # The malus is: stress +5, self_esteem -3, npc_Elena_trust -2
    # Il Performante has Neuroticism 30, so stress multiplier is 0.5 + 30/50 = 1.1
    # 5 * 1.1 = 5.5 -> 5
    # Narcissism 40, self_esteem decrement multiplier is 1 + 40/50 = 1.8
    # -3 * 1.8 = -5.4 -> -5

    assert agent.engine.player.stress > initial_stress
    assert agent.engine.player.self_esteem < initial_self_esteem
    assert agent.engine.player.npcs["Elena"].trust < initial_elena_trust

    print(f"Stress: {initial_stress} -> {agent.engine.player.stress}")
    print(f"Self-Esteem: {initial_self_esteem} -> {agent.engine.player.self_esteem}")
    print(f"Elena Trust: {initial_elena_trust} -> {agent.engine.player.npcs['Elena'].trust}")

if __name__ == "__main__":
    test_jump_penalty()
