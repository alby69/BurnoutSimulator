from dataclasses import dataclass, field
from typing import Dict, List, Set

@dataclass
class NPC:
    name: str
    role: str
    trust: int = 50
    fear: int = 0
    respect: int = 50

@dataclass
class Player:
    name: str
    company_type: str = "Corporate Tossica"
    energy: int = 100
    stress: int = 0
    self_esteem: int = 50
    manager_rep: int = 50
    team_rep: int = 50
    integrity: int = 50
    employability: int = 50
    health: int = 100

    # Factions: Loyalist, Silent, Rebel
    factions: Dict[str, int] = field(default_factory=lambda: {
        "Fedelissimi": 0,
        "Gruppo Silenzioso": 50,
        "Ribelli": 0
    })

    # NPCs
    npcs: Dict[str, NPC] = field(default_factory=lambda: {
        "Marco": NPC("Marco", "Manager Tossico"),
        "Giulia": NPC("Giulia", "Collega Opportunista"),
        "Roberto": NPC("Roberto", "Mentor Disilluso"),
        "Elena": NPC("Elena", "HR Passiva")
    })

    tags: Dict[str, int] = field(default_factory=lambda: {
        "yes_man": 0,
        "boundary_setter": 0,
        "truth_teller": 0,
        "survivor": 0,
        "burnout_risk": 0
    })

    achievements: Set[str] = field(default_factory=set)
    days_survived: int = 0
    is_alive: bool = True
    status: str = "Active"
    career_phase: str = "Periodo di Prova"
    decision_times: List[float] = field(default_factory=list)

    def update_stats(self, effects: dict, manager_traits: dict = None, psych_profile = None, hr_params: dict = None):
        # Calcolo bonus di fazione (Social Support)
        # Se l'agente è ben integrato in una fazione forte, riceve un bonus alla resistenza allo stress.
        # Se è isolato (punteggi bassi ovunque), è più vulnerabile.
        social_support = 0
        if any(v > 60 for v in self.factions.values()):
            social_support = 0.2 # 20% di riduzione stress
        elif all(v < 25 for v in self.factions.values()):
            social_support = -0.2 # 20% di aumento stress (vulnerabilità sociale)

        for stat, value in effects.items():
            # Se abbiamo un profilo psicologico, moduliamo la variazione (Scontro RPG)
            if psych_profile and not stat.startswith("npc_") and not stat.startswith("faction_") and stat != "reputation":
                value = psych_profile.modulate_stat_change(stat, value, manager_traits, hr_params)

            if stat == "stress" and value > 0:
                value = int(value * (1 - social_support))

            if stat == "reputation":
                self.manager_rep = max(0, min(100, self.manager_rep + value))
            elif hasattr(self, stat) and not isinstance(getattr(self, stat), (dict, list, set, NPC)):
                current_val = getattr(self, stat)
                setattr(self, stat, max(0, min(100, current_val + value)))
            elif stat.startswith("npc_"):
                # npc_Marco_trust
                parts = stat.split("_")
                if len(parts) == 3:
                    npc_name = parts[1]
                    attr = parts[2]
                    if npc_name in self.npcs:
                        npc = self.npcs[npc_name]
                        if hasattr(npc, attr):
                            current_val = getattr(npc, attr)
                            setattr(npc, attr, max(0, min(100, current_val + value)))
            elif stat.startswith("faction_"):
                # faction_Ribelli
                faction_name = stat.replace("faction_", "").replace("_", " ")
                if faction_name in self.factions:
                    self.factions[faction_name] = max(0, min(100, self.factions[faction_name] + value))

        self.check_conditions()

    def add_tags(self, tags_list: list):
        for tag in tags_list:
            if tag in self.tags:
                self.tags[tag] += 1
            else:
                self.tags[tag] = 1

        # Check for tag-based achievements
        t = self.tags
        if t.get("yes_man", 0) >= 10:
            self.achievements.add("Sempre Disponibile")
        if t.get("yes_man", 0) >= 20:
            self.achievements.add("Zerbino Ufficiale")
        if t.get("burnout_risk", 0) >= 5:
            self.achievements.add("Vivere al Limite")
        if t.get("burnout_risk", 0) >= 10:
            self.achievements.add("Combustione Lenta")
        if t.get("truth_teller", 0) >= 8:
            self.achievements.add("La Voce della Coscienza")
        if t.get("truth_teller", 0) >= 15:
            self.achievements.add("Senza Filtro")
        if t.get("boundary_setter", 0) >= 8:
            self.achievements.add("Confini Sani")
        if t.get("boundary_setter", 0) >= 15:
            self.achievements.add("Muro di Berlino")
        if t.get("survivor", 0) >= 10:
            self.achievements.add("Sopravvissuto")
        if t.get("survivor", 0) >= 20:
            self.achievements.add("Indistruttibile")
        if self.days_survived >= 30:
            self.achievements.add("Veterano")
        if self.days_survived >= 60:
            self.achievements.add("Leggenda Vivente")

    def check_conditions(self):
        if self.health <= 0:
            self.is_alive = False
            self.status = "Burnout (Crollo Fisico)"
        elif self.stress >= 100:
            self.is_alive = False
            self.status = "Burnout (Crollo Mentale)"
        elif self.energy <= 0:
            self.is_alive = False
            self.status = "Esaurimento Energie"
        elif self.manager_rep <= 0:
            self.is_alive = False
            self.status = "Licenziato"
        elif self.self_esteem <= 0:
            self.is_alive = False
            self.status = "Depressione Professionale"
        elif self.integrity <= 0:
            self.is_alive = False
            self.status = "Promozione Tossica"
        elif self.manager_rep >= 90 and self.days_survived >= 20:
            self.is_alive = False
            self.status = "Promosso"
        elif self.days_survived >= 365:
            self.is_alive = False
            self.status = "Sopravvissuto"

    def to_dict(self):
        return {
            "name": self.name,
            "company_type": self.company_type,
            "stats": {
                "energy": self.energy,
                "stress": self.stress,
                "self_esteem": self.self_esteem,
                "manager_rep": self.manager_rep,
                "team_rep": self.team_rep,
                "integrity": self.integrity,
                "employability": self.employability,
                "health": self.health
            },
            "factions": self.factions,
            "npcs": {name: vars(npc) for name, npc in self.npcs.items()},
            "tags": self.tags,
            "achievements": list(self.achievements),
            "days_survived": self.days_survived,
            "status": self.status
        }
