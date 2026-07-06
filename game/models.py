from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any

class Strategy(Enum):
    COMPLIANCE = "COMPLIANCE"
    RESISTANCE = "RESISTANCE"
    NEGOTIATION = "NEGOTIATION"
    ESCAPE = "ESCAPE"

class CompanyArchetype(Enum):
    STARTUP = "Startup Caotica"
    CORPORATE = "Corporate Tossica"
    FAMILY = "Azienda Familiare"
    CONSULTING = "Consulting"

class Faction(Enum):
    LOYALISTS = "Fedelissimi"
    SILENT = "Gruppo Silenzioso"
    REBELS = "Ribelli"

@dataclass
class NPCState:
    name: str
    role: str
    trust: int = 50
    fear: int = 0
    respect: int = 50

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "trust": self.trust,
            "fear": self.fear,
            "respect": self.respect
        }

@dataclass
class PlayerState:
    name: str
    company_type: CompanyArchetype = CompanyArchetype.CORPORATE
    energy: int = 100
    stress: int = 0
    self_esteem: int = 50
    manager_rep: int = 50
    team_rep: int = 50
    integrity: int = 50
    employability: int = 50
    health: int = 100
    factions: Dict[str, int] = field(default_factory=lambda: {
        Faction.LOYALISTS.value: 0,
        Faction.SILENT.value: 50,
        Faction.REBELS.value: 0
    })
    npcs: Dict[str, NPCState] = field(default_factory=dict)
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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "company_type": self.company_type.value,
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
            "npcs": {name: npc.to_dict() for name, npc in self.npcs.items()},
            "tags": self.tags,
            "achievements": list(self.achievements),
            "days_survived": self.days_survived,
            "status": self.status
        }
