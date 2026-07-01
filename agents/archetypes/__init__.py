from agents.base_agent import BurnoutAgent
from agentmesh.core import MeshConfig
from engine.psych_engine import PsychologicalProfile

class NaiveOptimist(BurnoutAgent):
    def __init__(self, agent_id: str = "naive-optimist"):
        config = MeshConfig(
            agent_id=agent_id,
            agent_name="Naive Optimist",
            agent_description="Starts with high energy, prone to rapid burnout."
        )
        profile = PsychologicalProfile(
            openness=80,
            conscientiousness=70,
            extraversion=70,
            agreeableness=90,
            neuroticism=30,
            resilience=40
        )
        super().__init__(config, profile)

class CynicalSurvivor(BurnoutAgent):
    def __init__(self, agent_id: str = "cynical-survivor"):
        config = MeshConfig(
            agent_id=agent_id,
            agent_name="Cynical Survivor",
            agent_description="High machiavellianism, survives at the cost of cynicism."
        )
        profile = PsychologicalProfile(
            agreeableness=30,
            machiavellianism=80,
            resilience=80,
            depersonalization=60
        )
        super().__init__(config, profile)
