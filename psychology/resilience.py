from pydantic import BaseModel
from typing import List

class ResilienceFactors(BaseModel):
    internal_locus: float
    social_connectedness: float
    self_efficacy: float

class ResilienceModel:
    """
    Fattori resilienza e capacità di recupero.
    """
    def calculate_resilience(self, factors: ResilienceFactors) -> float:
        return (factors.internal_locus + factors.social_connectedness + factors.self_efficacy) / 3
