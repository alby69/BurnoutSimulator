from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import random
import uuid

from .agent import Agent
from .personality import AGENT_PROFILES, PsychologicalProfile
from human.human_player import HumanPlayer
from database.agent_db import (
    save_agent,
    save_decision,
    save_jump,
    save_human_profile,
    save_swarm_session,
    get_all_agents,
    get_all_human_profiles,
)


class AgentSwarm:
    """
    Gestisce il laboratorio di agenti. Coordina la simulazione,
    i possessi umani e la visualizzazione.
    """

    def __init__(self, num_agents: int = 6):
        self.session_id: str = f"swarm_{uuid.uuid4().hex[:8]}"
        self.agents: Dict[str, Agent] = {}
        self.humans: Dict[str, HumanPlayer] = {}
        self.simulation_running: bool = False
        self.turn_counter: int = 0

        # Inizializza agenti con profili diversi
        self._init_agents(num_agents)

        # Salva sessione swarm
        save_swarm_session(
            {
                "session_id": self.session_id,
                "num_agents": num_agents,
                "started_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def _init_agents(self, num_agents: int):
        """Crea agenti con profili psicologici diversi."""
        profiles = list(AGENT_PROFILES.values())
        archetypes = [
            "Startup Caotica",
            "Corporate Tossica",
            "Azienda Familiare",
            "Consulting",
        ]

        for i in range(num_agents):
            profile = profiles[i % len(profiles)]
            archetype = archetypes[i % len(archetypes)]

            agent_id = f"agent_{uuid.uuid4().hex[:8]}"
            agent = Agent(
                agent_id=agent_id,
                name=f"{profile.name} #{i + 1}",
                profile=profile,
                company_type=archetype,
            )
            agent.initialize_game()
            self.agents[agent_id] = agent
            save_agent(agent.to_dict())

    def set_archetype_for_all(self, company_type: str):
        """
        Re-inizializza tutti gli agenti dello swarm con lo stesso archetype aziendale.
        Utile quando l'utente sceglie un'archetipo nella schermata iniziale
        e vuole che tutti gli agenti del laboratorio condividano lo stesso contesto.
        """
        for agent in self.agents.values():
            agent.company_type = company_type
            agent.initialize_game()
            save_agent(agent.to_dict())

    def register_human(self, name: str = "Osservatore") -> HumanPlayer:
        """Registra un nuovo giocatore umano."""
        human = HumanPlayer(name=name)
        self.humans[human.human_id] = human
        save_human_profile(human.to_dict())
        return human

    def get_available_agents(self, human_id: str) -> List[Dict]:
        """
        Restituisce agenti disponibili per il possesso.
        Esclude quelli già posseduti da altri umani.
        """
        available = []
        for agent_id, agent in self.agents.items():
            if agent.is_possessed and agent.possessed_by != human_id:
                continue  # Già posseduto da altro umano

            available.append(
                {
                    "agent_id": agent_id,
                    "name": agent.name,
                    "profile": {
                        "name": agent.profile.name,
                        "description": agent.profile.description,
                        "preferred_faction": agent.profile.preferred_faction,
                        "compliance_bias": agent.profile.compliance_bias,
                        "resistance_bias": agent.profile.resistance_bias,
                    },
                    "company_type": agent.company_type,
                    "current_day": agent.engine.player.days_survived
                    if agent.engine
                    else 0,
                    "is_alive": agent.engine.player.is_alive if agent.engine else False,
                    "is_possessed": agent.is_possessed,
                    "possessed_by": agent.possessed_by,
                    "current_stats": agent.engine.player.to_dict()["stats"]
                    if agent.engine
                    else None,
                    "current_factions": dict(agent.engine.player.factions)
                    if agent.engine
                    else None,
                    "match_score": self._calculate_match_score(human_id, agent)
                    if human_id in self.humans
                    else 50,
                }
            )

        # Ordina per "match" con il profilo umano
        available.sort(key=lambda x: x["match_score"], reverse=True)
        return available

    def _calculate_match_score(self, human_id: str, agent: Agent) -> int:
        """
        Calcola un punteggio di affinità tra l'umano e l'agente.
        Basato sulle scelte passate dell'umano vs il profilo dell'agente.
        """
        if human_id not in self.humans:
            return 50

        human = self.humans[human_id]
        profile = human.get_emergent_profile()

        score = 50  # Base

        # Confronta categorie preferite con bias dell'agente
        cat_dist = profile.get("category_distribution", {})

        # Se l'umano preferisce RESISTANCE, agenti con alto resistance_bias matchano meglio
        if cat_dist.get("RESISTANCE", 0) > 30:
            score += (agent.profile.resistance_bias - 30) // 2

        if cat_dist.get("COMPLIANCE", 0) > 30:
            score += (agent.profile.compliance_bias - 50) // 2

        if cat_dist.get("ESCAPE", 0) > 30:
            score += (agent.profile.escape_bias - 20) // 2

        # Penalizza agenti già provati (esplorazione)
        tried = set(j.to_agent_id for j in human.jump_history)
        if agent.agent_id in tried:
            score -= 10

        return max(0, min(100, score))

    def possess_agent(
        self, human_id: str, agent_id: str, reason: Optional[str] = None
    ) -> Dict:
        """
        Un umano prende possesso di un agente.
        """
        if human_id not in self.humans or agent_id not in self.agents:
            return {"error": "Human or agent not found"}

        human = self.humans[human_id]
        agent = self.agents[agent_id]

        # Calcola from_day: il giorno in cui l'umano ha INIZIATO a possedere l'agente precedente
        # to_day: il giorno attuale dell'agente precedente
        from_day = human.current_join_day
        to_day = 0
        if human.current_agent_id and human.current_agent_id in self.agents:
            old_agent = self.agents[human.current_agent_id]
            to_day = old_agent.engine.player.days_survived if old_agent.engine else 0
            old_agent.release(human_id)
            save_agent(old_agent.to_dict())

        # Possess nuovo agente
        current_agent_day = agent.engine.player.days_survived if agent.engine else 0
        jump_record = human.jump_to(
            from_agent_id=human.current_agent_id,
            to_agent_id=agent_id,
            from_day=from_day,
            to_day=to_day,
            reason=reason,
        )
        human.current_join_day = current_agent_day

        # Persistenza salto e profili
        save_jump(
            {
                "human_id": human_id,
                "from_agent_id": jump_record.from_agent_id,
                "to_agent_id": jump_record.to_agent_id,
                "from_day": jump_record.from_day,
                "to_day": jump_record.to_day,
                "reason": jump_record.reason,
                "declared_mood": jump_record.declared_mood,
                "timestamp": jump_record.timestamp,
            }
        )
        save_human_profile(human.to_dict())

        result = agent.possess(human_id)
        save_agent(agent.to_dict())

        return {
            "success": True,
            "jump_recorded": True,
            "agent_state": result,
            "human_profile": human.get_emergent_profile(),
        }

    def human_make_choice(self, human_id: str, choice_idx: int) -> Dict:
        """L'umano fa una scelta per l'agente posseduto."""
        if human_id not in self.humans:
            return {"error": "Human not found"}

        human = self.humans[human_id]
        if not human.current_agent_id:
            return {"error": "No agent possessed"}

        agent = self.agents[human.current_agent_id]

        # Esegui scelta
        event_before = agent.engine.current_event
        success = agent.human_chooses(choice_idx, human_id)

        if success:
            # Registra nel profilo umano
            if event_before and choice_idx < len(event_before.choices):
                choice = event_before.choices[choice_idx]
                human.record_choice_made(
                    agent.agent_id, choice.category, agent.engine.player.days_survived
                )

                # Persistenza decisione e profili
                save_human_profile(human.to_dict())
                save_agent(agent.to_dict())

            # Passa al prossimo turno
            if not agent.engine.is_game_over():
                agent.engine.next_turn()
                save_agent(agent.to_dict())

            return {
                "success": True,
                "next_event": agent.engine.current_event,
                "stats": agent.engine.player.to_dict(),
                "is_game_over": agent.engine.is_game_over(),
            }

        return {"error": "Choice failed"}

    def run_simulation_step(self) -> Dict:
        """
        Fa avanzare tutti gli agenti NON posseduti di un turno.
        Chiamato periodicamente o manualmente.
        """
        results = []
        for agent_id, agent in self.agents.items():
            if not agent.is_possessed and agent.engine and agent.engine.player.is_alive:
                event = agent.auto_play_turn()
                results.append(
                    {
                        "agent_id": agent_id,
                        "day": agent.engine.player.days_survived if agent.engine else 0,
                        "alive": agent.engine.player.is_alive
                        if agent.engine
                        else False,
                        "event": event.id if event else None,
                    }
                )
                save_agent(agent.to_dict())

        self.turn_counter += 1

        # Aggiorna sessione swarm
        save_swarm_session(
            {
                "session_id": self.session_id,
                "num_agents": len(self.agents),
                "total_turns": self.turn_counter,
            }
        )

        return {
            "turn": self.turn_counter,
            "agents_updated": len(results),
            "results": results,
        }

    def get_laboratory_view(self, human_id: Optional[str] = None) -> Dict:
        """
        Vista d'insieme del laboratorio per l'osservatore umano.
        """
        agents_view = []
        for agent_id, agent in self.agents.items():
            if not agent.engine:
                continue

            p = agent.engine.player
            agents_view.append(
                {
                    "agent_id": agent_id,
                    "name": agent.name,
                    "profile_name": agent.profile.name,
                    "company_type": agent.company_type,
                    "day": p.days_survived,
                    "alive": p.is_alive,
                    "status": p.status,
                    "is_possessed": agent.is_possessed,
                    "possessed_by": agent.possessed_by,
                    "stress": p.stress,
                    "energy": p.energy,
                    "health": p.health,
                    "dominant_faction": max(p.factions, key=p.factions.get),
                    "current_event": agent.engine.current_event.id
                    if agent.engine.current_event
                    else None,
                    "match_score": self._calculate_match_score(human_id, agent)
                    if human_id
                    else 50,
                }
            )

        # Ordina: prima quelli posseduti, poi per match score
        agents_view.sort(key=lambda x: (not x["is_possessed"], -x["match_score"]))

        return {
            "total_agents": len(self.agents),
            "alive_agents": sum(1 for a in agents_view if a["alive"]),
            "possessed_agents": sum(1 for a in agents_view if a["is_possessed"]),
            "agents": agents_view,
            "human_profile": self.humans[human_id].get_emergent_profile()
            if human_id and human_id in self.humans
            else None,
        }

    def get_agent_detailed_view(self, agent_id: str) -> Dict:
        """Vista dettagliata di un singolo agente (per decidere se saltare)."""
        if agent_id not in self.agents:
            return {"error": "Agent not found"}

        agent = self.agents[agent_id]
        return {
            "agent": agent.to_dict(),
            "memory_summary": agent.memory.get_summary(),
            "possession_history": [
                {
                    "human_id": p["human_id"],
                    "started": p["started_at"],
                    "ended": p["ended_at"],
                    "decisions": len(p["decisions_made"]),
                }
                for p in agent.possession_history
            ],
        }

    def load_swarm(self):
        """Ripristina lo stato dello sciame dal database."""
        # Carica Agenti
        db_agents = get_all_agents()
        if db_agents:
            self.agents = {}
            for da in db_agents:
                profile_name = da["profile_name"]
                profile = next(
                    (p for p in AGENT_PROFILES.values() if p.name == profile_name),
                    list(AGENT_PROFILES.values())[0],
                )

                agent = Agent(
                    agent_id=da["agent_id"],
                    name=da["name"],
                    profile=profile,
                    company_type=da["company_type"],
                )
                # Inizializza engine con lo stato salvato
                agent.initialize_game()
                # Se l'agente era vivo e ha stats salvate, dovremmo ripristinarle
                # Per ora ripartiamo dal giorno salvato o reinizializziamo
                if da["days_survived"] > 0:
                    agent.engine.player.days_survived = da["days_survived"]

                self.agents[da["agent_id"]] = agent
            print(f"Loaded {len(self.agents)} agents from DB")

        # Carica Umani
        db_humans = get_all_human_profiles()
        for dh in db_humans:
            human = HumanPlayer(human_id=dh["human_id"], name=dh["name"])
            # Carica dati aggiuntivi se necessario (jump_history etc)
            self.humans[dh["human_id"]] = human
            print(f"Loaded human {dh['name']} from DB")

    def get_swarm_analytics(self) -> Dict:
        """Statistiche globali del laboratorio."""
        if not self.agents:
            return {}

        total_decisions = sum(a.total_decisions for a in self.agents.values())
        avg_stress = sum(
            a.engine.player.stress for a in self.agents.values() if a.engine
        ) / len(self.agents)

        # Archetipo più stressante
        archetype_stress = {}
        for a in self.agents.values():
            if not a.engine:
                continue
            arch = a.company_type
            if arch not in archetype_stress:
                archetype_stress[arch] = []
            archetype_stress[arch].append(a.engine.player.stress)

        most_stressful = (
            max(archetype_stress.items(), key=lambda x: sum(x[1]) / len(x[1]))
            if archetype_stress
            else (None, 0)
        )

        return {
            "total_decisions": total_decisions,
            "avg_stress": round(avg_stress, 1),
            "most_stressful_archetype": most_stressful[0],
            "archetype_avg_stress": {
                k: round(sum(v) / len(v), 1) for k, v in archetype_stress.items()
            },
            "possessed_count": sum(1 for a in self.agents.values() if a.is_possessed),
            "alive_count": sum(
                1 for a in self.agents.values() if a.engine and a.engine.player.is_alive
            ),
        }
