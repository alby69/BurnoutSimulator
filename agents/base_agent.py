import asyncio
import logging
from typing import List, Optional, Dict, Any
from agentmesh.core import MeshConfig
from agentmesh.core.models import AgentMessage
from agentmesh.relay import NostrAgent
from engine.psych_engine import PsychologicalProfile, PsychometricEngine

class BurnoutAgent(NostrAgent):
    """
    Standard agent for BurnoutSimulator v3.0.
    Integrates psychological profiling with autonomous decision making
    and P2P coordination via Nostr.
    """

    def __init__(self, config: MeshConfig, secret_key: Optional[str] = None, profile: Optional[PsychologicalProfile] = None):
        super().__init__(config, secret_key=secret_key)
        self.profile = profile or PsychologicalProfile()
        self.psych_engine = PsychometricEngine()
        self.memory: List[Dict[str, Any]] = []
        self.logger.info(f"BurnoutAgent {config.agent_name} initialized with profile.")

    async def perceive(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Filters the event through the agent's psychological profile."""
        perceived_event = event_data.copy()
        if self.profile.neuroticism > 70:
            perceived_event["perceived_threat_level"] = "high"
        else:
            perceived_event["perceived_threat_level"] = "normal"
        return perceived_event

    async def decide(self, choices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Decision making logic based on profile and history."""
        if not choices:
            return {}

        if self.profile.agreeableness > 70:
            return min(choices, key=lambda c: c.get("effects", {}).get("stress", 0))

        if self.profile.machiavellianism > 60:
            return max(choices, key=lambda c: c.get("effects", {}).get("manager_rep", 0))

        import random
        return random.choice(choices)

    async def learn(self, outcome_data: Dict[str, Any]):
        """Update profile and memory based on outcome."""
        self.memory.append(outcome_data)
        self.profile = self.psych_engine.evaluate_choice(
            self.profile,
            outcome_data.get("choice", {}),
            outcome_data.get("context", {})
        )
        self.logger.info(f"Agent {self.config.agent_name} learned from outcome. New stress: {self.profile.current_stress}")

    async def handle_message(self, message: AgentMessage):
        """Handle A2A communication (Kind 29001)."""
        await super().handle_message(message)
        if message.message_type == "advice":
            self.logger.info(f"Received advice from {message.sender}: {message.content}")
            # Potentially adjust profile or decision weights based on advice
