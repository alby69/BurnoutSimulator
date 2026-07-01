from .base_agent import BaseAgent, Situation, Action
from typing import List, Dict, Any, Optional

class AIAgent(BaseAgent):
    """
    Agente completamente autonomo gestito dall'AI.
    Utilizza LLM per decisioni complesse + behavior tree per azioni routinarie.
    """

    def __init__(self, agent_id: str, profile: 'PsychologicalProfile', archetype: str, company_role: str):
        super().__init__(agent_id, profile)
        self.archetype = archetype
        self.company_role = company_role

    def generate_internal_monologue(self) -> str:
        """
        Genera un monologo interno che spiega il ragionamento.
        """
        # TODO: Integrare con LLM
        return f"Come {self.archetype}, mi sento {self.profile.stress_level} stressato."

    def decide(self, situation: Situation) -> Action:
        # Logica di esempio
        return situation.available_actions[0] if situation.available_actions else Action(type="wait", parameters={})
