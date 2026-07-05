import unittest
from agents.personality import PsychologicalProfile, AGENT_PROFILES
from agents.memory import AgentMemory
from agents.agent import Agent
from agents.swarm import AgentSwarm
from human.human_player import HumanPlayer

class TestAgentFramework(unittest.TestCase):
    def test_personality_weights(self):
        profile = AGENT_PROFILES["il_performante"]
        # Mock choices
        class MockChoice:
            def __init__(self, category, effects):
                self.category = category
                self.effects = effects

        choices = [
            MockChoice("COMPLIANCE", {"stress": 5}),
            MockChoice("ESCAPE", {"energy": 2})
        ]

        weights = profile.get_choice_weights(choices)
        self.assertEqual(len(weights), 2)
        # Il Performante has compliance_bias=70 and escape_bias=10
        self.assertGreater(weights[0], weights[1])

    def test_agent_initialization(self):
        profile = AGENT_PROFILES["il_sopravvissuto"]
        agent = Agent(agent_id="test_agent", name="Test Agent", profile=profile)
        self.assertEqual(agent.name, "Test Agent")
        self.assertFalse(agent.is_possessed)

    def test_swarm_initialization(self):
        swarm = AgentSwarm(num_agents=3)
        swarm.load_swarm(force_reinit=True)
        self.assertEqual(len(swarm.agents), 3)

    def test_human_jump(self):
        swarm = AgentSwarm(num_agents=2)
        swarm.load_swarm(force_reinit=True)
        human = swarm.register_human(name="Test Human")
        agent_ids = list(swarm.agents.keys())

        # Possess first agent
        res1 = swarm.possess_agent(human.human_id, agent_ids[0])
        self.assertTrue(res1["success"])
        self.assertEqual(human.current_agent_id, agent_ids[0])
        self.assertTrue(swarm.agents[agent_ids[0]].is_possessed)

        # Jump to second agent
        res2 = swarm.possess_agent(human.human_id, agent_ids[1], reason="Test jump")
        self.assertTrue(res2["success"])
        self.assertEqual(human.current_agent_id, agent_ids[1])
        self.assertFalse(swarm.agents[agent_ids[0]].is_possessed)
        self.assertTrue(swarm.agents[agent_ids[1]].is_possessed)
        self.assertEqual(len(human.jump_history), 2) # First possession counts as a jump from None

if __name__ == "__main__":
    unittest.main()
