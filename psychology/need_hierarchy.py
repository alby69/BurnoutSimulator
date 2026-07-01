from pydantic import BaseModel
from typing import List, Dict

class NeedHierarchy:
    """
    Gerarchia bisogni lavorativi adattata da Maslow e Deci & Ryan.
    Monitora quanto i bisogni fondamentali sono soddisfatti nell'ambiente di lavoro.
    """

    def evaluate_fulfillment(self, profile: 'PsychologicalProfile') -> Dict[str, float]:
        return {
            "autonomy": profile.autonomy_need,
            "competence": profile.competence_need,
            "relatedness": profile.relatedness_need
        }
