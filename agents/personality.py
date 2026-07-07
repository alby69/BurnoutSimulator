from dataclasses import dataclass, field
from typing import Dict, List, Optional
import random


@dataclass
class PsychologicalProfile:
    """
    Profilo psicologico basato su standard internazionali (Big Five e Dark Triad).
    Definisce come un agente reagisce e come interagisce con gli altri.
    """

    name: str
    description: str

    # --- Modello BIG FIVE (OCEAN) ---
    # 0-100
    openness: int = 50  # Apertura all'esperienza
    conscientiousness: int = 50  # Coscienziosità
    extraversion: int = 50  # Estroversione
    agreeableness: int = 50  # Gradevolezza (Empatia/Cooperazione)
    neuroticism: int = 50  # Nevroticismo (Stabilità emotiva inversa)

    # --- Modello TRIADE OSCURA ---
    # 0-100
    narcissism: int = 10  # Narcisismo
    machiavellianism: int = 10  # Machiavellismo
    psychopathy: int = 5  # Psicopatia

    # --- Bias categoria scelta (derivati o specifici) ---
    compliance_bias: int = 50  # Tendenza a COMPLIANCE
    resistance_bias: int = 30  # Tendenza a RESISTANCE
    negotiation_bias: int = 40  # Tendenza a NEGOTIATION
    escape_bias: int = 20  # Tendenza a ESCAPE

    # Legacy stats (kept for compatibility, will be linked to OCEAN)
    risk_tolerance: int = 50
    loyalty: int = 50
    assertiveness: int = 50
    resilience: int = 50
    cynicism: int = 30

    # Fazioni preferite
    preferred_faction: Optional[str] = None

    # Relazioni iniziali con NPC (override dei default)
    npc_relations: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # Trigger emozionali (eventi che attivano reazioni forti)
    emotional_triggers: List[str] = field(default_factory=list)

    # Peer influence accumulatore (quanto altri agenti influenzano questo profilo)
    _peer_influence_buffer: Dict[str, float] = field(
        default_factory=lambda: {
            "openness": 0.0,
            "conscientiousness": 0.0,
            "extraversion": 0.0,
            "agreeableness": 0.0,
            "neuroticism": 0.0,
        }
    )

    def __post_init__(self):
        """Sincronizza le statistiche legacy con OCEAN se non specificate diversamente."""
        # Se resilience non è stata toccata (default 50), usiamo (100 - neuroticism)
        if self.resilience == 50:
            self.resilience = 100 - self.neuroticism

        # Se loyalty non è toccata, influenzata da Conscientiousness e Agreeableness
        if self.loyalty == 50:
            self.loyalty = (self.conscientiousness + self.agreeableness) // 2

        # Assertiveness legata a Extraversion
        if self.assertiveness == 50:
            self.assertiveness = self.extraversion

        # Cynicism legato a Psychopathy e basso Agreeableness
        if self.cynicism == 30:
            self.cynicism = (self.psychopathy + (100 - self.agreeableness)) // 2

    def evolve(self, choice_category: str, outcome_deltas: Dict[str, int]):
        """
        Evolve i tratti della personalità in base alle scelte e ai loro esiti.
        Un timido (bassa estroversione) potrebbe diventare meno timido se le sue scelte portano a buoni esiti.
        """
        # Esempio: Se l'agente sceglie RESISTANCE e ottiene un aumento di autostima, aumenta l'extraversion (coraggio)
        if choice_category == "RESISTANCE":
            if outcome_deltas.get("self_esteem", 0) > 0:
                self.extraversion = min(100, self.extraversion + 2)
                self.neuroticism = max(0, self.neuroticism - 1)
            else:
                # Se la resistenza fallisce (perde autostima), aumenta il nevroticismo
                self.neuroticism = min(100, self.neuroticism + 2)

        # Se sceglie COMPLIANCE spesso, aumenta la coscienziosità ma cala l'apertura
        if choice_category == "COMPLIANCE":
            self.conscientiousness = min(100, self.conscientiousness + 1)
            self.openness = max(0, self.openness - 1)

        # Se lo stress è alto per molto tempo, aumenta il nevroticismo e cala l'agreeableness (cinismo)
        if outcome_deltas.get("stress", 0) > 5:
            self.neuroticism = min(100, self.neuroticism + 1)
            if self.neuroticism > 70:
                self.agreeableness = max(0, self.agreeableness - 1)

        # Sincronizza statistiche legacy
        self.__post_init__()

    def peer_influence(
        self,
        other_profiles: List["PsychologicalProfile"],
        proximity_weights: List[float],
    ):
        """
        Peer Influence Avanzata: gli agenti influenzano i tratti OCEAN
        degli agenti vicini nello sciame.
        `other_profiles`: lista di profili degli altri agenti
        `proximity_weights`: quanto ogni agente influenza questo (0-1)
        """
        trait_keys = [
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        ]
        for other, weight in zip(other_profiles, proximity_weights):
            for trait in trait_keys:
                diff = getattr(other, trait) - getattr(self, trait)
                influence = diff * weight * 0.02  # max 2% shift per turno
                self._peer_influence_buffer[trait] += influence

    def apply_peer_influence_buffer(self):
        """Applica il buffer di peer influence accumulato."""
        for trait, delta in self._peer_influence_buffer.items():
            current = getattr(self, trait)
            setattr(self, trait, max(0, min(100, current + delta)))
        self._peer_influence_buffer = {k: 0.0 for k in self._peer_influence_buffer}
        self.__post_init__()

    def to_dict(self) -> Dict:
        """Serializza il profilo per la persistenza."""
        return {
            "name": self.name,
            "description": self.description,
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
            "narcissism": self.narcissism,
            "machiavellianism": self.machiavellianism,
            "psychopathy": self.psychopathy,
            "compliance_bias": self.compliance_bias,
            "resistance_bias": self.resistance_bias,
            "negotiation_bias": self.negotiation_bias,
            "escape_bias": self.escape_bias,
            "resilience": self.resilience,
            "loyalty": self.loyalty,
            "assertiveness": self.assertiveness,
            "cynicism": self.cynicism,
            "preferred_faction": self.preferred_faction,
            "_peer_influence_buffer": self._peer_influence_buffer,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "PsychologicalProfile":
        """Crea un profilo da un dizionario."""
        buf = data.pop("_peer_influence_buffer", None)
        obj = cls(**data)
        if buf:
            obj._peer_influence_buffer = buf
        return obj

    def modulate_stat_change(
        self,
        stat: str,
        value: int,
        manager_traits: Optional[Dict] = None,
        hr_params: Optional[Dict] = None,
    ) -> int:
        """
        Modula la variazione di una statistica in base ai tratti dell'agente, del manager e parametri HR.
        Implementa la logica "RPG" di scontro tra valori.
        """
        if value == 0:
            return 0

        multiplier = 1.0

        # Parametri HR globali
        if hr_params:
            # Se la Tossicità Ambientale è alta, ogni aumento di stress è amplificato
            if stat == "stress" and value > 0:
                multiplier *= 1 + hr_params.get("toxicity", 0) / 100

            # Se la Coesione Sociale è alta, le perdite di salute/energia sono ridotte
            if stat in ["health", "energy"] and value < 0:
                multiplier *= 1 - hr_params.get("cohesion", 0) / 200

            # Pressione Risorse: aumenta il consumo di energia
            if stat == "energy" and value < 0:
                multiplier *= 1 + hr_params.get("pressure", 0) / 100

            # Competizione Interna: erode la reputazione nel team e l'autostima
            if stat in ["team_rep", "self_esteem"] and value < 0:
                multiplier *= 1 + hr_params.get("competition", 0) / 100

        # Interazione con Manager (Scontro RPG)
        if manager_traits:
            m_psychopathy = manager_traits.get("psychopathy", 0)
            m_machiavellianism = manager_traits.get("machiavellianism", 0)

            # Se il manager è psicopatico, colpi allo stress e integrità sono amplificati
            # specialmente per agenti "Gradevoli" (Empatici)
            if m_psychopathy > 50:
                if (value > 0 and stat == "stress") or (
                    value < 0 and stat in ["integrity", "self_esteem"]
                ):
                    multiplier *= 1 + (m_psychopathy / 100) * (self.agreeableness / 100)

            # Machiavellismo del manager erode l'energia se l'agente è molto Coscienzioso (lo sfrutta)
            if m_machiavellianism > 50 and stat == "energy" and value < 0:
                multiplier *= 1 + (m_machiavellianism / 100) * (
                    self.conscientiousness / 100
                )

        # Tratti intrinseci dell'agente
        if value > 0:  # Incremento
            if stat == "stress":
                # Più alto il nevroticismo, più aumenta lo stress
                multiplier *= 0.5 + self.neuroticism / 50
            if stat == "self_esteem":
                # Narcisisti guadagnano più autostima da successi/elogi
                multiplier *= 1 + self.narcissism / 100
        else:  # Decremento
            if stat == "health" or stat == "energy":
                # Bassa resilienza (alto nevroticismo) fa perdere più salute/energia
                multiplier *= 0.5 + self.neuroticism / 50
            if stat == "integrity":
                # Alta gradevolezza soffre di più la perdita di integrità
                multiplier *= self.agreeableness / 50
            if stat == "self_esteem":
                # Narcisisti perdono più autostima se colpiti (ferita narcisistica)
                multiplier *= 1 + self.narcissism / 50

        return int(value * multiplier)

    def get_choice_weights(self, choices: List) -> List[float]:
        """
        Calcola pesi per ogni scelta basandosi sul profilo psicometrico.
        """
        weights = []
        for choice in choices:
            weight = 1.0

            # 1. Bias per categoria basato su OCEAN/Dark Triad
            if choice.category == "COMPLIANCE":
                # Alti in Coscienziosità e Gradevolezza tendono a compiacere
                # Alti in Narcisismo tendono a compiacere se porta visibilità (assunto qui come base)
                cat_weight = (
                    self.conscientiousness * 0.4
                    + self.agreeableness * 0.4
                    + self.compliance_bias * 0.2
                ) / 50
            elif choice.category == "RESISTANCE":
                # Bassa Gradevolezza, alta Estroversione (Assertività) e Machiavellismo (se utile)
                cat_weight = (
                    (100 - self.agreeableness) * 0.3
                    + self.extraversion * 0.3
                    + self.machiavellianism * 0.2
                    + self.resistance_bias * 0.2
                ) / 50
            elif choice.category == "NEGOTIATION":
                # Alta Apertura e Gradevolezza
                cat_weight = (
                    self.openness * 0.4
                    + self.agreeableness * 0.4
                    + self.negotiation_bias * 0.2
                ) / 50
            elif choice.category == "ESCAPE":
                # Alto Nevroticismo e bassa Estroversione
                cat_weight = (
                    self.neuroticism * 0.5
                    + (100 - self.extraversion) * 0.3
                    + self.escape_bias * 0.2
                ) / 50
            else:
                cat_weight = 1.0

            weight *= max(0.2, cat_weight)

            # 2. Reazione agli effetti (Loss Aversion basata su Neuroticism)
            for stat, val in choice.effects.items():
                if val < 0:  # Effetto negativo
                    # Più alto il nevroticismo, più pesano gli effetti negativi
                    weight *= 1 - (self.neuroticism / 200)
                if stat == "integrity" and val < 0:
                    # Persone con alta gradevolezza o bassa psicopatia evitano di perdere integrità
                    weight *= (self.agreeableness / 50) * (1 - self.psychopathy / 100)

            weights.append(max(0.1, weight))

        return weights


# --- PROFILI STANDARD RIFORMULATI ---
AGENT_PROFILES = {
    "il_performante": PsychologicalProfile(
        name="Il Performante",
        description="Orientato al successo e alla carriera. Alta coscienziosità, narcisismo moderato.",
        openness=60,
        conscientiousness=85,
        extraversion=70,
        agreeableness=40,
        neuroticism=30,
        narcissism=40,
        machiavellianism=30,
        compliance_bias=70,
        preferred_faction="Fedelissimi",
    ),
    "il_protettore": PsychologicalProfile(
        name="Il Protettore",
        description="Difende il team. Alta gradevolezza e bassa psicopatia.",
        openness=50,
        conscientiousness=60,
        extraversion=65,
        agreeableness=90,
        neuroticism=40,
        narcissism=10,
        machiavellianism=10,
        resistance_bias=70,
        preferred_faction="Ribelli",
    ),
    "il_sopravvissuto": PsychologicalProfile(
        name="Il Sopravvissuto",
        description="Evita conflitti. Alto nevroticismo, bassa estroversione.",
        openness=40,
        conscientiousness=50,
        extraversion=30,
        agreeableness=50,
        neuroticism=75,
        escape_bias=80,
        preferred_faction="Gruppo Silenzioso",
    ),
    "il_negotiatore": PsychologicalProfile(
        name="Il Negoziatore",
        description="Cerca compromessi. Alta apertura e gradevolezza.",
        openness=80,
        conscientiousness=60,
        extraversion=60,
        agreeableness=75,
        neuroticism=35,
        negotiation_bias=90,
    ),
    "il_cinico": PsychologicalProfile(
        name="Il Cinico",
        description="Disilluso e distaccato. Bassa gradevolezza, alto machiavellismo.",
        openness=50,
        conscientiousness=40,
        extraversion=40,
        agreeableness=20,
        neuroticism=50,
        machiavellianism=60,
        psychopathy=30,
        escape_bias=60,
        preferred_faction="Gruppo Silenzioso",
    ),
    "il_manipolatore": PsychologicalProfile(
        name="Il Manipolatore",
        description="Usa le persone per i propri fini. Triade Oscura elevata.",
        openness=60,
        conscientiousness=70,
        extraversion=75,
        agreeableness=15,
        neuroticism=20,
        narcissism=70,
        machiavellianism=85,
        psychopathy=50,
        negotiation_bias=60,
        preferred_faction="Fedelissimi",
    ),
    "l_idealista": PsychologicalProfile(
        name="L'Idealista",
        description="Valori incrollabili. Alta apertura, bassa gradevolezza verso il male.",
        openness=90,
        conscientiousness=70,
        extraversion=50,
        agreeableness=60,  # Molto gradevole con chi merita, ma...
        neuroticism=55,
        resistance_bias=85,
        preferred_faction="Ribelli",
    ),
}
