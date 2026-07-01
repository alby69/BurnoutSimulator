from dataclasses import dataclass, field
from typing import Dict, List, Optional
import json

@dataclass
class PsychologicalProfile:
    # Big Five (OCEAN)
    openness: float = 50.0          # 0-100: creativity, curiosity vs conventionality
    conscientiousness: float = 50.0 # 0-100: organization, self-discipline
    extraversion: float = 50.0      # 0-100: social energy, assertiveness
    agreeableness: float = 50.0     # 0-100: cooperation, empathy vs competition
    neuroticism: float = 50.0       # 0-100: emotional instability, anxiety

    # Dark Triad
    machiavellianism: float = 10.0  # 0-100: strategic manipulation
    narcissism: float = 10.0        # 0-100: need for admiration
    psychopathy: float = 5.0        # 0-100: impulsivity, lack of empathy

    # Workplace-specific
    resilience: float = 50.0        # 0-100: recovery capacity
    locus_of_control: float = 50.0  # 0-100: internal (active) vs external (passive)
    psychological_safety: float = 50.0 # 0-100: perception of safety in team

    # Dynamic state
    current_stress: float = 0.0
    cognitive_load: float = 0.0
    emotional_exhaustion: float = 0.0
    depersonalization: float = 0.0  # cynicism towards colleagues/work
    personal_accomplishment: float = 50.0  # sense of achievement

    def to_dict(self):
        return vars(self)

class PsychometricEngine:
    def __init__(self, ontology_path: str = "engine/data/keywords_ontology.json"):
        self.ontology = self._load_ontology(ontology_path)
        self.choice_history = []

    def _load_ontology(self, path: str) -> Dict:
        try:
            with open(path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def evaluate_choice(self, player_profile: PsychologicalProfile, choice_data: Dict, context: Dict) -> PsychologicalProfile:
        """
        Updates the psychological profile based on the choice and context.
        In v3.0, this will use a Dynamic Bayesian Network or LLM-based evaluation.
        For now, we implement a refined rule-based mapping.
        """
        effects = choice_data.get("effects", {})
        tags = choice_data.get("tags", [])

        # Update dynamic states from direct effects
        player_profile.current_stress = max(0, min(100, player_profile.current_stress + effects.get("stress", 0)))
        player_profile.emotional_exhaustion = max(0, min(100, player_profile.emotional_exhaustion + (effects.get("stress", 0) * 0.5)))

        # Tag-based mapping to Big Five / Dark Triad
        for tag in tags:
            if tag == "yes_man":
                player_profile.agreeableness = min(100, player_profile.agreeableness + 1)
                player_profile.conscientiousness = min(100, player_profile.conscientiousness + 0.5)
                player_profile.neuroticism = min(100, player_profile.neuroticism + 0.5)
            elif tag == "boundary_setter":
                player_profile.extraversion = min(100, player_profile.extraversion + 1)
                player_profile.agreeableness = max(0, player_profile.agreeableness - 0.5)
                player_profile.resilience = min(100, player_profile.resilience + 1)
            elif tag == "truth_teller":
                player_profile.conscientiousness = min(100, player_profile.conscientiousness + 1)
                player_profile.agreeableness = max(0, player_profile.agreeableness - 0.5)
            elif tag == "survivor":
                player_profile.resilience = min(100, player_profile.resilience + 1)
                player_profile.machiavellianism = min(100, player_profile.machiavellianism + 0.5)

        return player_profile

    def calculate_burnout_risk(self, profile: PsychologicalProfile) -> float:
        """
        Calculates risk based on Maslach Burnout Inventory components.
        Risk = (Emotional Exhaustion + Depersonalization + (100 - Personal Accomplishment)) / 3
        """
        risk = (profile.emotional_exhaustion + profile.depersonalization + (100 - profile.personal_accomplishment)) / 3
        return max(0, min(100, risk))
