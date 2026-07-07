from typing import Dict, Any, Optional
import random

class PhenomenologyEngine:
    """
    Gestisce la fenomenologia dello sfinimento e la percezione alterata della realtà
    in base allo stato corporeo, temporale e spaziale dell'agente.
    """

    def __init__(self):
        # Definizioni degli stati fenomenologici e dei loro impatti
        self.states = {
            "insomnia": {
                "threshold": 60,
                "description": "Insonnia cronica: la realtà appare sfocata e ostile.",
                "perception_modifier": 1.5, # Eventi visti come più minacciosi
                "energy_drain": 5
            },
            "muscle_tension": {
                "threshold": 50,
                "description": "Tensione muscolare: ogni movimento è fatica, il corpo è un'armatura rigida.",
                "stress_multiplier": 1.2
            },
            "digestive_issues": {
                "threshold": 40,
                "description": "Somatizzazione gastrica: ansia viscerale costante.",
                "mood_impact": -10
            },
            "time_distortion_crunch": {
                "threshold": 80, # Stress alto
                "description": "Crunch time: il tempo accelera, il futuro scompare nel presente continuo.",
                "distortion": 1.5
            },
            "atmosphere_suffocating": {
                "threshold": 30, # Atmosfera bassa
                "description": "Atmosfera soffocante: l'aria in ufficio è densa e irrespirabile.",
                "integrity_drain": 2
            }
        }

    def update_phenomenology(self, player: Any) -> Dict[str, Any]:
        """Aggiorna lo stato fenomenologico basandosi sulle statistiche base."""
        # Logica di somatizzazione: lo stress si trasforma in parametri corporei
        if player.stress > 50:
            player.insomnia = min(100, player.insomnia + random.randint(1, 5))
            player.muscle_tension = min(100, player.muscle_tension + random.randint(2, 6))
        else:
            player.insomnia = max(0, player.insomnia - 2)
            player.muscle_tension = max(0, player.muscle_tension - 3)

        if player.energy < 30:
            player.digestive_issues = min(100, player.digestive_issues + 5)

        # Atmosfera collettiva (qui semplificata, influenzata dalla reputazione e stress)
        player.atmosphere_feeling = max(0, min(100, 100 - (player.stress * 0.7 + (100 - player.manager_rep) * 0.3)))

        # Time distortion based on stress/energy
        if player.stress > 80:
            player.time_distortion = 1.5
        elif player.energy < 20:
            player.time_distortion = 0.5 # Tempo rallentato, sfinimento
        else:
            player.time_distortion = 1.0

        return self.get_active_phenomenological_reports(player)

    def get_active_phenomenological_reports(self, player: Any) -> Dict[str, Any]:
        reports = {}
        if player.insomnia >= self.states["insomnia"]["threshold"]:
            reports["insomnia"] = self.states["insomnia"]["description"]
        if player.muscle_tension >= self.states["muscle_tension"]["threshold"]:
            reports["muscle_tension"] = self.states["muscle_tension"]["description"]
        if player.digestive_issues >= self.states["digestive_issues"]["threshold"]:
            reports["digestive_issues"] = self.states["digestive_issues"]["description"]
        if player.time_distortion > 1.2:
            reports["time"] = self.states["time_distortion_crunch"]["description"]
        if player.atmosphere_feeling <= self.states["atmosphere_suffocating"]["threshold"]:
            reports["atmosphere"] = self.states["atmosphere_suffocating"]["description"]

        return reports

    def modulate_event_impact(self, player: Any, effects: Dict[str, int]) -> Dict[str, int]:
        """Modula l'impatto degli eventi in base allo stato fenomenologico."""
        modulated_effects = effects.copy()

        # Se ha insonnia, lo stress aumenta di più
        if player.insomnia >= self.states["insomnia"]["threshold"]:
            if "stress" in modulated_effects and modulated_effects["stress"] > 0:
                modulated_effects["stress"] = int(modulated_effects["stress"] * self.states["insomnia"]["perception_modifier"])

        # Se l'atmosfera è soffocante, la perdita di integrità è maggiore
        if player.atmosphere_feeling <= self.states["atmosphere_suffocating"]["threshold"]:
            if "integrity" in modulated_effects and modulated_effects["integrity"] < 0:
                modulated_effects["integrity"] = int(modulated_effects["integrity"] * 1.3)

        return modulated_effects
