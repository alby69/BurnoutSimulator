from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from enum import Enum

class DevianceType(str, Enum):
    TOSSICITA_ORGANIZZATIVA = "TOSSICITA_ORGANIZZATIVA"
    AUTOLESIONISMO_LAVORATIVO = "AUTOLESIONISMO_LAVORATIVO"
    ISOLAMENTO_SOCIALE = "ISOLAMENTO_SOCIALE"
    AGGRESSIVITA_PASSIVA = "AGGRESSIVITA_PASSIVA"
    CONFORMISMO_TOSSICO = "CONFORMISMO_TOSSICO"

class DevianceReport(BaseModel):
    type: DevianceType
    severity: float
    pattern_description: str
    involved_agents: List[str]
    trend: str # "increasing", "stable", "decreasing"

class ManagementOptions(BaseModel):
    recommended_action: str
    risk_of_escalation: float

class DevianceDetector:
    """
    Identifica comportamenti devianti (negativi per il benessere)
    e propone modalità di gestione.
    """

    def detect_deviance(self, agent_id: str, history: List[Any]) -> List[DevianceReport]:
        # TODO: Implementare pattern matching su behavior history
        return []

    def propose_management(self, deviance: DevianceReport) -> ManagementOptions:
        # TODO: Implementare logica di suggerimento intervento
        return ManagementOptions(
            recommended_action="REDIRECT: Pilotare verso altre direzioni",
            risk_of_escalation=0.2
        )
