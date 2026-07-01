from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import uuid


@dataclass
class JumpRecord:
    """Registra un salto da un agente a un altro."""
    from_agent_id: str
    to_agent_id: str
    from_day: int
    to_day: int
    reason: Optional[str] = None  # Motivazione del salto (opzionale, per analytics)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Stato emotivo dichiarato al momento del salto
    declared_mood: Optional[str] = None
    declared_stress: Optional[int] = None


@dataclass
class HumanPlayer:
    """
    Il giocatore umano che osserva il laboratorio di agenti
    e salta tra di loro.
    """
    human_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = "Osservatore"

    # Storia dei salti
    jump_history: List[JumpRecord] = field(default_factory=list)

    # Agente attualmente posseduto
    current_agent_id: Optional[str] = None
    current_join_day: int = 0

    # Percorso psicologico emergente
    psychological_trace: List[Dict] = field(default_factory=list)

    # Preferenze apprese
    preferred_categories: Dict[str, int] = field(default_factory=lambda: {
        "COMPLIANCE": 0,
        "RESISTANCE": 0,
        "NEGOTIATION": 0,
        "ESCAPE": 0
    })

    def jump_to(self, from_agent_id: Optional[str], to_agent_id: str,
                from_day: int, to_day: int, reason: Optional[str] = None,
                declared_mood: Optional[str] = None) -> JumpRecord:
        """
        Esegue un salto da un agente a un altro.
        from_day / to_day sono l'inizio e la fine della permanenza sull'agente VECCHIO.
        """
        jump = JumpRecord(
            from_agent_id=from_agent_id,
            to_agent_id=to_agent_id,
            from_day=from_day,
            to_day=to_day,
            reason=reason,
            declared_mood=declared_mood
        )
        self.jump_history.append(jump)
        self.current_agent_id = to_agent_id
        # Nota: current_join_day deve essere aggiornato dal chiamante (swarm)

        # Aggiorna traccia psicologica
        self.psychological_trace.append({
            "timestamp": datetime.now().isoformat(),
            "from_agent_id": from_agent_id,
            "to_agent_id": to_agent_id,
            "stay_duration": to_day - from_day,
            "mood": declared_mood,
            "jump_number": len(self.jump_history)
        })

        return jump

    def record_choice_made(self, agent_id: str, choice_category: str, day: int):
        """Aggiorna il profilo emergente basato sulle scelte fatte."""
        if choice_category in self.preferred_categories:
            self.preferred_categories[choice_category] += 1

        self.psychological_trace.append({
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "day": day,
            "action": "choice",
            "category": choice_category
        })

    def get_emergent_profile(self) -> Dict:
        """
        Calcola il profilo psicologico emergente dell'umano
        basato sulle sue scelte e salti.
        """
        total = sum(self.preferred_categories.values()) or 1

        # Determina profilo dominante
        dominant = max(self.preferred_categories, key=self.preferred_categories.get)

        # Calcola "affinità" con ogni agente
        return {
            "dominant_category": dominant,
            "category_distribution": {
                k: round(v / total * 100, 1)
                for k, v in self.preferred_categories.items()
            },
            "total_jumps": len(self.jump_history),
            "unique_agents_played": len(set(
                j.to_agent_id for j in self.jump_history
            )),
            "avg_stay_duration": self._avg_stay_duration(),
            "jump_pattern": self._analyze_jump_pattern(),
            "jump_history": [
                {"day": j.to_day, "to": j.to_agent_id, "mood": j.declared_mood}
                for j in self.jump_history
            ]
        }

    def _avg_stay_duration(self) -> float:
        """Calcola la durata media basata sui salti completati (escluso il primo se nullo)."""
        durations = [j.to_day - j.from_day for j in self.jump_history if j.from_agent_id is not None]
        if not durations:
            return 0
        return sum(durations) / len(durations)

    def _analyze_jump_pattern(self) -> str:
        """Analizza il pattern di salto."""
        if len(self.jump_history) < 2:
            return "insufficient_data"

        # Controlla se salta quando lo stress è alto
        stress_jumps = sum(1 for j in self.jump_history
                          if j.declared_mood and "stress" in j.declared_mood.lower())

        if stress_jumps > len(self.jump_history) * 0.5:
            return "stress_avoider"

        # Controlla se esplora molti agenti diversi
        unique = len(set(j.to_agent_id for j in self.jump_history))
        if unique > len(self.jump_history) * 0.7:
            return "explorer"

        return "selective"

    def to_dict(self) -> Dict:
        return {
            "human_id": self.human_id,
            "name": self.name,
            "current_agent": self.current_agent_id,
            "total_jumps": len(self.jump_history),
            "emergent_profile": self.get_emergent_profile(),
            "jump_history": [
                {
                    "from": j.from_agent_id,
                    "to": j.to_agent_id,
                    "day": j.to_day,
                    "reason": j.reason,
                    "mood": j.declared_mood
                }
                for j in self.jump_history
            ]
        }
