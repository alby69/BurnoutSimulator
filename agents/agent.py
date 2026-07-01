from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import random
import json

from game.engine import GameEngine
from .personality import PsychologicalProfile, AGENT_PROFILES
from .memory import AgentMemory


@dataclass
class Agent:
    """
    Un agente autonomo che gioca BurnoutSimulator con un proprio profilo psicologico.
    Può giocare in automatico o essere "posseduto" da un giocatore umano.
    """
    agent_id: str
    name: str
    profile: PsychologicalProfile
    company_type: str = "Corporate Tossica"

    # Stato di gioco
    engine: Optional[GameEngine] = field(default=None, repr=False)

    # Memoria storica
    memory: AgentMemory = field(default_factory=lambda: AgentMemory())

    # Stato possesso umano
    is_possessed: bool = False           # True se un umano sta controllando
    possessed_by: Optional[str] = None   # ID umano
    possession_history: List[Dict] = field(default_factory=list)

    # Metadati
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    total_decisions: int = 0
    auto_decisions: int = 0

    def initialize_game(self, events_file: str = "game/data/events.json"):
        """Inizializza una nuova partita per questo agente."""
        self.engine = GameEngine(
            player_name=self.name,
            events_file=events_file,
            company_type=self.company_type
        )
        # Applica relazioni NPC custom dal profilo
        for npc_name, relations in self.profile.npc_relations.items():
            if npc_name in self.engine.player.npcs:
                for attr, val in relations.items():
                    setattr(self.engine.player.npcs[npc_name], attr, val)

        self.engine.next_turn()
        return self.engine.current_event

    def decide(self, event) -> int:
        """
        L'agente sceglie automaticamente in base al suo profilo psicologico.
        Restituisce l'indice della scelta.
        """
        if not event or not event.choices:
            return 0

        weights = self.profile.get_choice_weights(event.choices)

        # Modifica pesi basata sulla memoria (agente impara dai propri errori)
        weights = self._apply_memory_weights(event, weights)

        # Modifica basata sullo stato attuale (agente "sensibile" allo stress)
        weights = self._apply_state_weights(weights)

        # Scelta pesata
        choice_idx = random.choices(
            range(len(event.choices)),
            weights=weights,
            k=1
        )[0]

        self.auto_decisions += 1
        self.total_decisions += 1

        # Registra nella memoria
        self.memory.record_decision(
            event_id=event.id,
            choice_id=event.choices[choice_idx].id,
            choice_text=event.choices[choice_idx].text,
            category=event.choices[choice_idx].category,
            was_auto=True
        )

        return choice_idx

    def _apply_memory_weights(self, event, weights: List[float]) -> List[float]:
        """Modifica pesi basandosi su esperienze passate simili."""
        for i, choice in enumerate(event.choices):
            # Se questa scelta ha portato a brutti risultati in passato, penalizza
            past_outcomes = self.memory.get_choice_outcomes(choice.id)
            if past_outcomes:
                avg_stress_change = sum(o.get('stress_delta', 0) for o in past_outcomes) / len(past_outcomes)
                if avg_stress_change > 5:
                    weights[i] *= 0.7  # Penalizza scelte stressanti
                if avg_stress_change < -3:
                    weights[i] *= 1.3  # Bonus scelte rilassanti
        return weights

    def _apply_state_weights(self, weights: List[float]) -> List[float]:
        """Modifica pesi basandosi sullo stato attuale del player."""
        if not self.engine:
            return weights

        p = self.engine.player

        # Se stress è alto, agenti con bassa resilienza tendono a ESCAPE
        if p.stress > 70:
            for i, choice in enumerate(self.engine.current_event.choices if self.engine.current_event else []):
                if choice.category == "ESCAPE":
                    weights[i] *= (1 + (100 - self.profile.resilience) / 100)

        # Se salute è bassa, qualsiasi agente evita danni alla salute
        if p.health < 30:
            for i, choice in enumerate(self.engine.current_event.choices if self.engine.current_event else []):
                if "health" in choice.effects and choice.effects["health"] < 0:
                    weights[i] *= 0.3

        return weights

    def possess(self, human_id: str) -> Dict:
        """
        Un umano prende il controllo di questo agente.
        Restituisce lo stato attuale per la UI.
        """
        self.is_possessed = True
        self.possessed_by = human_id

        possession_record = {
            "human_id": human_id,
            "started_at": datetime.now().isoformat(),
            "agent_state_at_possession": self._get_snapshot(),
            "ended_at": None,
            "decisions_made": []
        }
        self.possession_history.append(possession_record)

        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "profile": self.profile,
            "current_event": self.engine.current_event if self.engine else None,
            "player_stats": self.engine.player.to_dict() if self.engine else None,
            "day": self.engine.player.days_survived if self.engine else 0
        }

    def release(self, human_id: str):
        """L'umano rilascia il controllo. L'agente torna ad auto-giocare."""
        if self.possession_history:
            last = self.possession_history[-1]
            if last["human_id"] == human_id and last["ended_at"] is None:
                last["ended_at"] = datetime.now().isoformat()

        self.is_possessed = False
        self.possessed_by = None

    def human_chooses(self, choice_idx: int, human_id: str) -> bool:
        """Registra una scelta fatta dall'umano durante il possesso."""
        if not self.is_possessed or self.possessed_by != human_id:
            return False

        if not self.engine or not self.engine.current_event:
            return False

        choice = self.engine.current_event.choices[choice_idx]

        # Registra nella memoria come decisione umana
        self.memory.record_decision(
            event_id=self.engine.current_event.id,
            choice_id=choice.id,
            choice_text=choice.text,
            category=choice.category,
            was_auto=False,
            human_id=human_id
        )

        # Registra nel possesso attuale
        if self.possession_history:
            self.possession_history[-1]["decisions_made"].append({
                "turn": self.engine.player.days_survived,
                "event_id": self.engine.current_event.id,
                "choice_id": choice.id,
                "timestamp": datetime.now().isoformat()
            })

        self.total_decisions += 1

        # Esegui la scelta nel motore di gioco
        return self.engine.handle_choice(choice_idx)

    def auto_play_turn(self) -> Optional[Any]:
        """L'agente gioca un turno in automatico."""
        if self.is_possessed or not self.engine:
            return None

        event = self.engine.current_event
        if not event:
            return None

        choice_idx = self.decide(event)
        self.engine.handle_choice(choice_idx)

        if not self.engine.is_game_over():
            self.engine.next_turn()

        return self.engine.current_event

    def _get_snapshot(self) -> Dict:
        """Snapshot dello stato attuale."""
        return {
            "stats": self.engine.player.to_dict() if self.engine else None,
            "day": self.engine.player.days_survived if self.engine else 0,
            "factions": dict(self.engine.player.factions) if self.engine else None,
            "tags": dict(self.engine.player.tags) if self.engine else None,
        }

    def to_dict(self) -> Dict:
        """Serializzazione completa."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "profile_name": self.profile.name,
            "company_type": self.company_type,
            "is_possessed": self.is_possessed,
            "possessed_by": self.possessed_by,
            "total_decisions": self.total_decisions,
            "auto_decisions": self.auto_decisions,
            "created_at": self.created_at,
            "current_state": self._get_snapshot() if self.engine else None,
        }
