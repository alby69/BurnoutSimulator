from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class BehaviorRecord(BaseModel):
    timestamp: datetime
    action: str
    context: Dict[str, Any]
    impact: Dict[str, float]

class StressEvent(BaseModel):
    timestamp: datetime
    description: str
    intensity: float

class RecoveryPeriod(BaseModel):
    start_time: datetime
    end_time: datetime
    quality: float

class PsychologicalProfile(BaseModel):
    """
    Profilo psicologico dinamico basato su Big Five + bisogni lavorativi.
    Ogni agente (umano o AI) ha un profilo che evolve nel tempo.
    """

    # Big Five (0.0 - 1.0, evolvono)
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5

    # Bisogni lavorativi (modello Deci & Ryan - Autonomia, Competenza, Relazione)
    autonomy_need: float = 0.5        # 0.0 - 1.0
    competence_need: float = 0.5      # 0.0 - 1.0
    relatedness_need: float = 0.5     # 0.0 - 1.0

    # Stati dinamici
    stress_level: float = 0.0         # 0.0 - 1.0 (burnout > 0.75)
    engagement: float = 0.5           # 0.0 - 1.0
    job_satisfaction: float = 0.5     # 0.0 - 1.0
    work_life_balance: float = 0.5    # 0.0 - 1.0

    # Fattori protettivi
    resilience: float = 0.5           # Capacità di recupero
    social_support: float = 0.5       # Rete di supporto percepita
    coping_strategies: List[str] = Field(default_factory=list) # Strategie attive

    # Pattern storici
    behavior_history: List[BehaviorRecord] = Field(default_factory=list)
    stress_events: List[StressEvent] = Field(default_factory=list)
    recovery_periods: List[RecoveryPeriod] = Field(default_factory=list)

    def update_profile(self, delta: Dict[str, float]):
        """TODO: Implementare logica di aggiornamento basata su eventi"""
        pass
