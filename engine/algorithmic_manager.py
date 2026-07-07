from typing import Dict, Any, Optional
import random

class AlgorithmicManager:
    """
    Simula la governance algoritmica: monitoraggio opaco, nudging e analytics predittivi.
    """

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.productivity_score = 70
        self.burnout_prediction = 10
        self.surveillance_level = 50

    def process_turn(self, player_stats: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        # L'algoritmo calcola il punteggio di produttività basandosi sull'energia spesa
        # Ma è opaco e ingiusto
        energy = player_stats.get("energy", 50)
        stress = player_stats.get("stress", 0)

        # Se lo stress è alto, l'algoritmo 'nota' un calo di 'sentiment'
        self.burnout_prediction = stress + random.randint(-10, 10)

        # Nudging: se la produttività è bassa, invia una notifica
        nudges = []
        if energy < 40:
            self.productivity_score -= 5
            nudges.append("Notifica Algoritmica: 'La tua velocità di risposta è calata. Ricorda che il team conta su di te.'")

        if self.burnout_prediction > 80:
            nudges.append("Alert HR: 'Il sistema ha rilevato un rischio turnover. Il manager è stato informato per un intervento preventivo.'")

        return {
            "productivity_score": self.productivity_score,
            "prediction": self.burnout_prediction,
            "nudges": nudges
        }

    def modulate_impact(self, effects: Dict[str, int]) -> Dict[str, int]:
        if not self.enabled:
            return effects

        new_effects = effects.copy()
        # Sotto governance algoritmica, lo stress da compliance è più alto
        if "stress" in new_effects and new_effects["stress"] > 0:
            new_effects["stress"] = int(new_effects["stress"] * 1.2)

        return new_effects
