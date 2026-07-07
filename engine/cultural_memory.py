from typing import Dict, List, Any, Optional
import random

class OrganizationalMemory:
    """
    Gestisce la memoria culturale dell'organizzazione: storia, gossip, riti e artefatti.
    """

    def __init__(self, company_type: str):
        self.company_type = company_type
        self.institutional_history: List[str] = []
        self.rumors: List[str] = []
        self.rituals: List[str] = []
        self.artifacts: List[str] = []
        self._initialize_memory()

    def _initialize_memory(self):
        # Memorie specifiche per archetipo
        if self.company_type == "Startup Caotica":
            self.institutional_history = ["Fondata in un garage", "Il leggendario pivot del 2022"]
            self.artifacts = ["Il tavolo da ping pong mai usato", "L'adesivo della prima release"]
            self.rituals = ["Stand-up delle 9 di sera", "Pizza post-crunch"]
        elif self.company_type == "Corporate Tossica":
            self.institutional_history = ["La grande fusione del 2018", "Lo scandalo dei rimborsi"]
            self.artifacts = ["Il badge dorato dei top performer", "Il manuale di compliance di 400 pagine"]
            self.rituals = ["Performance review trimestrale", "Town hall obbligatoria"]

        self.rumors = [
            "Si dice che HR stia preparando un nuovo round di tagli.",
            "Gira voce che il manager stia per essere promosso... o licenziato.",
            "Dicono che Roberto abbia un dossier su tutti."
        ]

    def get_random_rumor(self) -> str:
        return random.choice(self.rumors)

    def add_event_to_history(self, event_description: str):
        self.institutional_history.append(event_description)
        if len(self.institutional_history) > 20:
            self.institutional_history.pop(0)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "history": self.institutional_history[-3:],
            "artifacts": self.artifacts,
            "rituals": self.rituals
        }
