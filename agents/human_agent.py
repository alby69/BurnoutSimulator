from .base_agent import BaseAgent, Action
from datetime import datetime
from typing import List

class HumanAgent(BaseAgent):
    """
    Wrapper per giocatori umani che interagiscono via mobile.
    """

    def __init__(self, agent_id: str, profile: 'PsychologicalProfile', device_id: str):
        super().__init__(agent_id, profile)
        self.device_id = device_id
        self.last_sync = datetime.now()
        self.pending_notifications: List[Dict] = []

    def receive_push(self, notification: Dict):
        self.pending_notifications.append(notification)

    def sync_state(self):
        self.last_sync = datetime.now()
        # TODO: Implementare logica di sincronizzazione
