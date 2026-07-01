from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random

@dataclass
class PsychologicalProfile:
    """
    Profilo psicologico che definisce come un agente "naturalmente" reagisce.
    Ogni agente ha un profilo che influenza le sue scelte automatiche.
    """
    name: str
    description: str

    # Bias categoria scelta (0-100, somma non deve essere 100)
    # Rappresenta la propensione naturale
    compliance_bias: int = 50      # Tendenza a COMPLIANCE
    resistance_bias: int = 30      # Tendenza a RESISTANCE
    negotiation_bias: int = 40     # Tendenza a NEGOTIATION
    escape_bias: int = 20          # Tendenza a ESCAPE

    # Bias statistico (como reagisce allo stress, ecc.)
    risk_tolerance: int = 50       # 0=cauto, 100=azzardato
    loyalty: int = 50              # 0=indipendente, 100=fedele all'azienda
    assertiveness: int = 50        # 0=passivo, 100=assertivo
    resilience: int = 50           # 0=fragile, 100=resiliente
    cynicism: int = 30             # 0=ingenuo, 100=cinico

    # Fazioni preferite (influenza scelte che muovono fazioni)
    preferred_faction: Optional[str] = None  # "Fedelissimi", "Ribelli", ecc.

    # Relazioni iniziali con NPC (override dei default)
    npc_relations: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # Trigger emozionali (eventi che attivano reazioni forti)
    emotional_triggers: List[str] = field(default_factory=list)

    def get_choice_weights(self, choices: List) -> List[float]:
        """
        Calcola pesi per ogni scelta disponibile basandosi sul profilo.
        """
        weights = []
        for choice in choices:
            weight = 1.0

            # Bias per categoria
            cat_bias = {
                "COMPLIANCE": self.compliance_bias,
                "RESISTANCE": self.resistance_bias,
                "NEGOTIATION": self.negotiation_bias,
                "ESCAPE": self.escape_bias,
            }.get(choice.category, 50)

            weight *= (cat_bias / 50)  # Normalizza su 1.0

            # Modifica per effetti sulla salute (agenti con bassa resilienza evitano danni)
            for stat, val in choice.effects.items():
                if stat == "health" and val < 0:
                    weight *= (1 + (100 - self.resilience) / 100 * 0.5)
                if stat == "stress" and val > 3:
                    weight *= (1 + (100 - self.resilience) / 100 * 0.3)

            weights.append(max(0.1, weight))  # Minimo 0.1 per evitare scelte impossibili

        return weights


# Profili predefiniti
AGENT_PROFILES = {
    "il_performante": PsychologicalProfile(
        name="Il Performante",
        description="Lavora per i risultati. Accetta pressioni se porta a riconoscimenti.",
        compliance_bias=70,
        resistance_bias=15,
        negotiation_bias=50,
        escape_bias=10,
        risk_tolerance=65,
        loyalty=70,
        assertiveness=60,
        resilience=55,
        preferred_faction="Fedelissimi",
        emotional_triggers=["valutazione_ingiusta", "appropriazione_idea"]
    ),

    "il_protettore": PsychologicalProfile(
        name="Il Protettore",
        description="Difende i colleghi e i confini. Rifiuta ingiustizie verso il team.",
        compliance_bias=30,
        resistance_bias=70,
        negotiation_bias=60,
        escape_bias=20,
        risk_tolerance=40,
        loyalty=60,
        assertiveness=75,
        resilience=60,
        preferred_faction="Ribelli",
        emotional_triggers=["capro_espiatorio", "commento_inappropriate", "collega_favorito_credito"]
    ),

    "il_sopravvissuto": PsychologicalProfile(
        name="Il Sopravvissuto",
        description="Fa il minimo indispensabile. Preserva energia e salute mentale.",
        compliance_bias=40,
        resistance_bias=20,
        negotiation_bias=40,
        escape_bias=80,
        risk_tolerance=25,
        loyalty=30,
        assertiveness=30,
        resilience=70,
        preferred_faction="Gruppo Silenzioso",
        emotional_triggers=["doppio_incarico", "compito_extra_non_pagato"]
    ),

    "il_negotiatore": PsychologicalProfile(
        name="Il Negoziatore",
        description="Cerca sempre il compromesso. Evita conflitti ma non si arrende.",
        compliance_bias=45,
        resistance_bias=35,
        negotiation_bias=90,
        escape_bias=30,
        risk_tolerance=50,
        loyalty=55,
        assertiveness=65,
        resilience=50,
        preferred_faction=None,
        emotional_triggers=["scadenza_impossibile", "valutazione_ingiusta"]
    ),

    "il_perfezionista": PsychologicalProfile(
        name="Il Perfezionista",
        description="Non accetta compromessi sulla qualità. Si sacrifica per il lavoro ben fatto.",
        compliance_bias=60,
        resistance_bias=40,
        negotiation_bias=50,
        escape_bias=15,
        risk_tolerance=45,
        loyalty=75,
        assertiveness=55,
        resilience=35,
        preferred_faction="Fedelissimi",
        emotional_triggers=["sabotaggio_progetto", "valutazione_ingiusta"]
    ),

    "il_cinico": PsychologicalProfile(
        name="Il Cinico",
        description="Ha visto troppo. Sceglie strategie ciniche, spesso ESCAPE o RESISTANCE passiva.",
        compliance_bias=20,
        resistance_bias=50,
        negotiation_bias=30,
        escape_bias=70,
        risk_tolerance=60,
        loyalty=15,
        assertiveness=40,
        resilience=80,
        preferred_faction="Gruppo Silenzioso",
        emotional_triggers=["pettegolezzi_ufficio", "taglio_benefit"]
    ),

    "il_idealista": PsychologicalProfile(
        name="L'Idealista",
        description="Credo nei valori. Rischia tutto per l'integrità e la giustizia.",
        compliance_bias=20,
        resistance_bias=85,
        negotiation_bias=40,
        escape_bias=25,
        risk_tolerance=70,
        loyalty=40,
        assertiveness=80,
        resilience=45,
        preferred_faction="Ribelli",
        emotional_triggers=["appropriazione_idea", "capro_espiatorio", "commento_inappropriate"]
    ),
}
