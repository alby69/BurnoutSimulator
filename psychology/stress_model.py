from pydantic import BaseModel
from typing import List, Optional
from .profile import PsychologicalProfile

class RiskAssessment(BaseModel):
    risk_score: float
    warning_signals: List[str]
    recommended_interventions: List[str]
    time_horizon: str  # e.g., "7 days", "24 hours"

class RecoveryProjection(BaseModel):
    expected_stress_reduction: float
    time_to_recovery: str

class DynamicStressModel:
    """
    Modello stress/burnout che considera:
    - Carico lavorativo oggettivo
    - Percezione soggettiva (filtrata dal profilo psicologico)
    - Fattori protettivi
    - Recupero (sonno, weekend, ferie)

    CRITICO: Il modello deve identificare il punto di non ritorno
    prima che avvenga. Non è predittivo in senso capitalistico,
    ma preventivo in senso umanistico.
    """

    def calculate_burnout_risk(self, profile: PsychologicalProfile) -> RiskAssessment:
        """
        Calcola il rischio di burnout basato sul profilo.
        """
        # Logica semplificata per ora
        risk_score = (profile.stress_level * 0.5 +
                      profile.neuroticism * 0.2 +
                      (1 - profile.resilience) * 0.3)

        signals = []
        if profile.stress_level > 0.7:
            signals.append("Livello di stress critico")
        if profile.work_life_balance < 0.3:
            signals.append("Squilibrio vita-lavoro grave")

        interventions = []
        if risk_score > 0.7:
            interventions.append("Pausa obbligatoria")
            interventions.append("Supporto psicologico")

        return RiskAssessment(
            risk_score=risk_score,
            warning_signals=signals,
            recommended_interventions=interventions,
            time_horizon="Prossimi 7 giorni"
        )

    def simulate_recovery(self, profile: PsychologicalProfile, intervention_type: str) -> RecoveryProjection:
        """
        Simula l'impatto di un intervento sul recupero.
        """
        # TODO: Implementare logica complessa
        return RecoveryProjection(
            expected_stress_reduction=0.2,
            time_to_recovery="48 ore"
        )
