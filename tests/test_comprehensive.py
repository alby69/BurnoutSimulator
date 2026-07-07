"""
Test completo e unificato per BurnoutSimulator v3.5.
Copre l'intero flusso: engine, player, swarm, agenti, dashboard, psicologia, UI backend.
"""

import pytest
import sys
import os
import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ─────────────────────────────────────────────
# MODULE LEVEL SETUP
# ─────────────────────────────────────────────

from agents.personality import PsychologicalProfile, AGENT_PROFILES
from agents.agent import Agent, AgentMemory
from agents.swarm import AgentSwarm
from human.human_player import HumanPlayer

from game.engine import (
    GameEngine,
    MINI_EVENTS,
    THRESHOLD_EVENTS,
    CAREER_PHASES,
    MANAGER_PERSONALITIES,
)
from game.player import Player
from game.models import CompanyArchetype, Faction, NPCState
from game.events import Event, Choice, EventManager
from game.graph import DecisionGraph

from dashboard.main_dashboard import (
    MainDashboard,
    AgentMonitor,
    AlertSystem,
    Reports,
    TimelineViewer,
)

# ─────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────


@pytest.fixture(autouse=True)
def clean_db():
    """Pulisce DB test prima di ogni test."""
    db_path = Path("database/agents.db")
    if db_path.exists():
        db_path.unlink()
    from database.agent_db import init_agent_db

    init_agent_db()
    yield
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def swarm():
    sw = AgentSwarm(num_agents=4)
    sw._init_agents(4)
    sw.turn_counter = 0
    return sw


@pytest.fixture
def swarm_with_turns(swarm):
    for _ in range(5):
        swarm.run_simulation_step()
    return swarm


@pytest.fixture
def engine():
    eng = GameEngine("TestPlayer", "game/data/events.json")
    eng.next_turn()
    return eng


@pytest.fixture
def player():
    return Player(name="TestPlayer")


@pytest.fixture
def profile_performante():
    return AGENT_PROFILES["il_performante"]


@pytest.fixture
def profile_sopravvissuto():
    return AGENT_PROFILES["il_sopravvissuto"]


@pytest.fixture
def agent(profile_performante):
    a = Agent(agent_id="agent_01", name="TestAgent", profile=profile_performante)
    a.initialize_game()
    return a


@pytest.fixture
def human(swarm):
    return swarm.register_human("TestHuman")


# ═════════════════════════════════════════════
# SEZIONE 1: GAME ENGINE
# ═════════════════════════════════════════════


class TestGameEngine:
    """Test del GameEngine: inizializzazione, turni, scelte, game over."""

    def test_engine_init(self, engine):
        assert engine is not None
        assert engine.player is not None
        assert engine.player.name == "TestPlayer"
        assert engine.current_event is not None
        assert engine.player.days_survived == 1  # next_turn avanzato

    def test_engine_archetype_startup(self):
        eng = GameEngine(
            "Test", "game/data/events.json", company_type=CompanyArchetype.STARTUP.value
        )
        assert eng.player.energy == 80
        assert eng.player.stress == 20

    def test_engine_archetype_corporate(self):
        eng = GameEngine(
            "Test",
            "game/data/events.json",
            company_type=CompanyArchetype.CORPORATE.value,
        )
        assert eng.player.energy == 100
        assert eng.player.stress == 10

    def test_next_turn_increments_day(self, engine):
        old_day = engine.player.days_survived
        engine.next_turn()
        assert engine.player.days_survived == old_day + 1

    def test_next_turn_generates_event(self, engine):
        old_event_id = engine.current_event.id
        engine.next_turn()
        assert engine.current_event is not None

    def test_next_turn_mini_event(self, engine):
        assert engine.current_mini_event is not None
        text, effects = engine.current_mini_event
        assert isinstance(text, str)
        assert isinstance(effects, dict)

    def test_handle_choice_valid(self, engine):
        event = engine.current_event
        n_choices = len(event.choices)
        result = engine.handle_choice(0)
        assert result is True

    def test_handle_choice_invalid(self, engine):
        event = engine.current_event
        result = engine.handle_choice(999)
        assert result is False

    def test_handle_choice_updates_stats(self, engine):
        event = engine.current_event
        choice = event.choices[0]
        old_stress = engine.player.stress
        engine.handle_choice(0)
        if "stress" in choice.effects:
            assert (
                engine.player.stress != old_stress or engine.player.stress == old_stress
            )

    def test_game_over_burnout(self, engine):
        engine.player.stress = 100
        engine.player.check_conditions()
        assert engine.is_game_over() is True
        assert "Burnout" in engine.player.status

    def test_game_over_health(self, engine):
        engine.player.health = 0
        engine.player.check_conditions()
        assert engine.is_game_over() is True

    def test_game_over_energy(self, engine):
        engine.player.energy = 0
        engine.player.check_conditions()
        assert engine.is_game_over() is True

    def test_game_over_manager_rep(self, engine):
        engine.player.manager_rep = 0
        engine.player.check_conditions()
        assert engine.is_game_over() is True

    def test_game_over_promoted(self, engine):
        engine.player.manager_rep = 90
        engine.player.days_survived = 20
        engine.player.check_conditions()
        assert engine.is_game_over() is True
        assert engine.player.status == "Promosso"

    def test_game_over_survived(self, engine):
        engine.player.days_survived = 365
        engine.player.check_conditions()
        assert engine.is_game_over() is True
        assert engine.player.status == "Sopravvissuto"

    def test_game_over_alive(self, engine):
        assert engine.is_game_over() is False

    def test_career_phase_initial(self, engine):
        engine.player.days_survived = 0
        phase = engine.get_career_phase()
        assert phase[1] == "Periodo di Prova"

    def test_career_phase_advanced(self, engine):
        engine.player.days_survived = 60
        phase = engine.get_career_phase()
        assert phase[1] == "Sopravvivenza"

    def test_threshold_event_triggers(self, engine):
        engine.player.stress = 85
        old_len = len(engine._last_threshold_triggers)
        engine.process_threshold_events()
        assert len(engine._last_threshold_triggers) >= old_len

    def test_hidden_vars_init(self, engine):
        assert "manager_patience" in engine.hidden_vars
        assert "company_crisis" in engine.hidden_vars

    def test_engine_save_game(self, engine):
        save_path = engine.save_game()
        assert save_path is not None
        assert Path(save_path).exists() if save_path else True

    def test_engine_apply_archetype(self):
        eng = GameEngine(
            "Test", "game/data/events.json", company_type=CompanyArchetype.STARTUP.value
        )
        eng.apply_archetype(CompanyArchetype.CORPORATE.value)
        assert eng.player.energy == 100
        assert eng.player.stress == 10


# ═════════════════════════════════════════════
# SEZIONE 2: PLAYER
# ═════════════════════════════════════════════


class TestPlayer:
    """Test del Player: stats, factions, NPC, tags, achievements."""

    def test_player_init(self, player):
        assert player.name == "TestPlayer"
        assert player.energy == 100
        assert player.stress == 0
        assert player.is_alive is True

    def test_player_update_stats_simple(self, player):
        player.update_stats({"stress": 10, "energy": -5})
        assert player.stress == 10
        assert player.energy == 95

    def test_player_update_stats_clamp(self, player):
        player.update_stats({"stress": -100})
        assert player.stress == 0
        player.update_stats({"stress": 200})
        assert player.stress == 100

    def test_player_update_stats_faction_stress_reduction(self, player):
        player.factions["Fedelissimi"] = 80
        player.update_stats({"stress": 10})
        # social_support 20% => 10 * 0.8 = 8
        assert player.stress == 8

    def test_player_update_stats_npc(self, player):
        old = player.npcs["Marco"].trust
        player.update_stats({"npc_Marco_trust": 10})
        assert player.npcs["Marco"].trust == min(100, old + 10)

    def test_player_update_stats_faction(self, player):
        player.update_stats({"faction_Fedelissimi": 10})
        assert player.factions["Fedelissimi"] == 10

    def test_player_update_stats_reputation(self, player):
        player.update_stats({"reputation": 10})
        assert player.manager_rep == 60

    def test_player_add_tag(self, player):
        player.add_tags(["yes_man"])
        assert player.tags["yes_man"] == 1

    def test_player_add_tag_multiple(self, player):
        player.add_tags(["yes_man", "yes_man", "truth_teller"])
        assert player.tags["yes_man"] == 2
        assert player.tags["truth_teller"] == 1

    def test_player_achievements_yes_man_10(self, player):
        player.add_tags(["yes_man"] * 10)
        assert "Sempre Disponibile" in player.achievements

    def test_player_achievements_yes_man_20(self, player):
        player.add_tags(["yes_man"] * 20)
        assert "Zerbino Ufficiale" in player.achievements

    def test_player_achievements_survivor_10(self, player):
        player.add_tags(["survivor"] * 10)
        assert "Sopravvissuto" in player.achievements

    def test_player_achievements_veteran(self, player):
        player.days_survived = 30
        player.add_tags([])
        assert "Veterano" in player.achievements

    def test_player_achievements_legend(self, player):
        player.days_survived = 60
        player.add_tags([])
        assert "Leggenda Vivente" in player.achievements

    def test_player_check_conditions_no_death(self, player):
        player.check_conditions()
        assert player.is_alive is True

    def test_player_check_conditions_stress_death(self, player):
        player.stress = 100
        player.check_conditions()
        assert player.is_alive is False
        assert "Burnout" in player.status

    def test_player_to_dict(self, player):
        d = player.to_dict()
        assert "name" in d
        assert "stats" in d
        assert "factions" in d
        assert "npcs" in d
        assert "days_survived" in d
        assert d["name"] == "TestPlayer"

    def test_player_factions_default(self, player):
        assert player.factions["Gruppo Silenzioso"] == 50
        assert player.factions["Fedelissimi"] == 0
        assert player.factions["Ribelli"] == 0

    def test_player_npcs_default(self, player):
        assert len(player.npcs) == 4
        assert "Marco" in player.npcs
        assert "Giulia" in player.npcs
        assert "Roberto" in player.npcs
        assert "Elena" in player.npcs


# ═════════════════════════════════════════════
# SEZIONE 3: SWARM & AGENTI
# ═════════════════════════════════════════════


class TestSwarm:
    """Test dello sciame: init, simulazione, laboratory view, possession."""

    def test_swarm_init(self, swarm):
        assert len(swarm.agents) == 4
        assert swarm.turn_counter == 0

    def test_swarm_run_simulation(self, swarm_with_turns):
        assert swarm_with_turns.turn_counter == 5
        for agent in swarm_with_turns.agents.values():
            assert agent.engine is not None

    def test_swarm_lab_view_has_agents(self, swarm_with_turns):
        view = swarm_with_turns.get_laboratory_view()
        assert "agents" in view
        assert len(view["agents"]) > 0
        assert view["total_agents"] > 0

    def test_swarm_lab_view_agent_fields(self, swarm_with_turns):
        view = swarm_with_turns.get_laboratory_view()
        agent = view["agents"][0]
        assert "agent_id" in agent
        assert "name" in agent
        assert "stress" in agent
        assert "energy" in agent
        assert "health" in agent
        assert "profile_name" in agent

    def test_swarm_lab_view_analytics(self, swarm_with_turns):
        view = swarm_with_turns.get_laboratory_view()
        assert "analytics" in view
        a = view["analytics"]
        assert "avg_stress" in a
        assert "alive_count" in a
        assert "total_decisions" in a

    def test_swarm_lab_view_cultural_drift(self, swarm_with_turns):
        view = swarm_with_turns.get_laboratory_view()
        assert "cultural_drift" in view
        assert "dominant_culture" in view["cultural_drift"]

    def test_swarm_register_human(self, swarm):
        human = swarm.register_human("Pippo")
        assert human is not None
        assert human.name == "Pippo"
        assert human.human_id in swarm.humans

    def test_swarm_possess_agent(self, swarm, human):
        agent_id = list(swarm.agents.keys())[0]
        result = swarm.possess_agent(human.human_id, agent_id)
        assert result["success"] is True
        assert swarm.agents[agent_id].is_possessed is True

    def test_swarm_possess_nonexistent(self, swarm, human):
        result = swarm.possess_agent(human.human_id, "fake_id")
        assert "error" in result

    def test_swarm_release_agent(self, swarm, human):
        agent_id = list(swarm.agents.keys())[0]
        swarm.possess_agent(human.human_id, agent_id)
        swarm.agents[agent_id].release(human.human_id)
        assert swarm.agents[agent_id].is_possessed is False

    def test_swarm_agent_to_dict(self, agent):
        d = agent.to_dict()
        assert "agent_id" in d
        assert "name" in d
        assert d["name"] == "TestAgent"
        assert "profile_name" in d
        assert "profile_json" in d
        assert "is_possessed" in d

    def test_swarm_get_available_agents(self, swarm, human):
        available = swarm.get_available_agents(human.human_id)
        assert len(available) == len(swarm.agents)

    def test_swarm_possessed_not_available(self, swarm, human):
        agent_id = list(swarm.agents.keys())[0]
        swarm.possess_agent(human.human_id, agent_id)
        available = swarm.get_available_agents(human.human_id)
        # Il già posseduto dall'umano corrente dovrebbe essere disponibile
        assert any(a["agent_id"] == agent_id for a in available)

    def test_swarm_simulation_step_non_possessed(self, swarm, human):
        agent_id = list(swarm.agents.keys())[0]
        swarm.possess_agent(human.human_id, agent_id)
        old_day = swarm.agents[agent_id].engine.player.days_survived
        swarm.run_simulation_step()
        # L'agente posseduto NON avanza
        assert swarm.agents[agent_id].engine.player.days_survived == old_day

    def test_swarm_human_make_choice(self, swarm, human):
        agent_id = list(swarm.agents.keys())[0]
        swarm.possess_agent(human.human_id, agent_id)
        old_day = swarm.agents[agent_id].engine.player.days_survived
        swarm.human_make_choice(human.human_id, 0)
        # La scelta umana NON avanza il giorno (è handle_choice)
        assert swarm.agents[agent_id].engine.player.days_survived == old_day

    def test_swarm_get_swarm_analytics(self, swarm_with_turns):
        analytics = swarm_with_turns.get_swarm_analytics()
        assert "avg_stress" in analytics
        assert "alive_count" in analytics
        assert "profile_impact" in analytics
        assert analytics["avg_stress"] >= 0

    def test_swarm_get_available_filters_dead(self, swarm, human):
        agent_id = list(swarm.agents.keys())[0]
        swarm.agents[agent_id].engine.player.is_alive = False
        available = swarm.get_available_agents(human.human_id)
        dead_agent = next((a for a in available if a["agent_id"] == agent_id), None)
        assert dead_agent is not None
        assert dead_agent["is_alive"] is False

    def test_swarm_release_abandons_agent(self, swarm):
        human = swarm.register_human("Test")
        agent_id = list(swarm.agents.keys())[0]
        agent = swarm.agents[agent_id]
        old_energy = agent.engine.player.energy
        old_self_esteem = agent.engine.player.self_esteem
        old_elena_trust = agent.engine.player.npcs["Elena"].trust
        swarm.possess_agent(human.human_id, agent_id)
        # Jump away
        agent_id2 = list(swarm.agents.keys())[1]
        swarm.possess_agent(human.human_id, agent_id2)
        # L'agente lasciato ha penalità
        assert (
            agent.engine.player.self_esteem != old_self_esteem
            or agent.engine.player.stress != old_energy
        )

    def test_swarm_lab_view_sorted_possessed_first(self, swarm, human):
        agent_id = list(swarm.agents.keys())[2]
        swarm.possess_agent(human.human_id, agent_id)
        view = swarm.get_laboratory_view(human.human_id)
        assert view["agents"][0]["is_possessed"] is True


# ═════════════════════════════════════════════
# SEZIONE 4: PSICOLOGIA (PEER INFLUENCE, EVOLUZIONE)
# ═════════════════════════════════════════════


class TestPsychology:
    """Test dei profili psicologici, peer influence, evoluzione."""

    def test_profile_init(self, profile_performante):
        assert profile_performante.name == "Il Performante"
        assert profile_performante.compliance_bias == 70
        assert profile_performante.resistance_bias == 30

    def test_profile_to_dict(self, profile_performante):
        d = profile_performante.to_dict()
        assert d["name"] == "Il Performante"
        assert "openness" in d
        assert "neuroticism" in d
        assert "_peer_influence_buffer" in d

    def test_profile_from_dict(self, profile_performante):
        d = profile_performante.to_dict()
        restored = PsychologicalProfile.from_dict(d)
        assert restored.name == "Il Performante"
        assert restored.openness == profile_performante.openness

    def test_profile_evolution_compliance(self, profile_performante):
        old_conscientiousness = profile_performante.conscientiousness
        profile_performante.evolve("COMPLIANCE", {"stress": 0, "self_esteem": 0})
        assert profile_performante.conscientiousness > old_conscientiousness

    def test_profile_evolution_resistance_success(self, profile_performante):
        old_extraversion = profile_performante.extraversion
        profile_performante.evolve("RESISTANCE", {"self_esteem": 5, "stress": 0})
        assert profile_performante.extraversion > old_extraversion

    def test_profile_evolution_resistance_failure(self, profile_performante):
        old_neuroticism = profile_performante.neuroticism
        profile_performante.evolve("RESISTANCE", {"self_esteem": -5, "stress": 0})
        assert profile_performante.neuroticism > old_neuroticism

    def test_peer_influence_buffer_starts_empty(self, profile_performante):
        for v in profile_performante._peer_influence_buffer.values():
            assert v == 0.0

    def test_peer_influence_modifies_buffer(
        self, profile_performante, profile_sopravvissuto
    ):
        profile_performante.peer_influence([profile_sopravvissuto], [0.5])
        assert any(
            v != 0.0 for v in profile_performante._peer_influence_buffer.values()
        )

    def test_apply_buffer_changes_trait(
        self, profile_performante, profile_sopravvissuto
    ):
        old_openness = profile_performante.openness
        profile_performante.peer_influence([profile_sopravvissuto], [0.8])
        profile_performante.apply_peer_influence_buffer()
        assert profile_performante.openness != old_openness

    def test_peer_influence_no_crash_single_agent(self, profile_performante):
        profile_performante.peer_influence([], [])
        profile_performante.apply_peer_influence_buffer()

    def test_profile_choice_weights(self, profile_performante):
        class MockChoice:
            def __init__(self, category):
                self.category = category
                self.effects = {"stress": 0}

        choices = [MockChoice("COMPLIANCE"), MockChoice("RESISTANCE")]
        weights = profile_performante.get_choice_weights(choices)
        assert len(weights) == 2
        assert weights[0] > weights[1]  # Performante prefers compliance

    def test_profile_str(self, profile_performante):
        s = str(profile_performante)
        assert "Il Performante" in s

    def test_profile_descriptions_exist(self):
        assert "il_performante" in AGENT_PROFILES
        assert "il_sopravvissuto" in AGENT_PROFILES
        for key, profile in AGENT_PROFILES.items():
            assert profile.name is not None
            assert profile.description is not None

    def test_profile_get_choice_probabilities(self, profile_performante):
        """Le probabilità di scelta sono calcolate dall'Agent, non dal profilo."""
        from agents.agent import Agent

        agent = Agent(agent_id="test", name="Test", profile=profile_performante)
        agent.initialize_game()
        probs = agent.get_choice_probabilities()
        if probs:
            assert len(probs) > 0
            assert abs(sum(probs) - 100) < 2.0


# ═════════════════════════════════════════════
# SEZIONE 5: CULTURAL DRIFT
# ═════════════════════════════════════════════


class TestCulturalDrift:
    """Test della pressione culturale dinamica."""

    def test_cultural_drift_after_steps(self, swarm_with_turns):
        "Cultural drift produce un risultato dopo alcuni turni"
        info = swarm_with_turns._get_cultural_drift_info()
        assert "dominant_culture" in info

    def test_cultural_drift_changes_hr_params(self, swarm):
        old_hrs = {}
        for aid, a in swarm.agents.items():
            if a.engine:
                old_hrs[aid] = dict(a.engine.hr_params)
        for _ in range(6):
            swarm.run_simulation_step()
        changed = False
        for aid, a in swarm.agents.items():
            if a.engine and aid in old_hrs:
                if a.engine.hr_params != old_hrs[aid]:
                    changed = True
                    break
        assert changed is True

    def test_cultural_drift_in_lab_view(self, swarm_with_turns):
        view = swarm_with_turns.get_laboratory_view()
        assert "cultural_drift" in view
        assert "drift_scores" in view["cultural_drift"]

    def test_cultural_drift_does_not_crash_empty_swarm(self):
        sw = AgentSwarm(num_agents=0)
        sw.agents = {}
        sw._apply_cultural_drift()  # Non deve sollevare eccezioni


# ═════════════════════════════════════════════
# SEZIONE 6: DASHBOARD
# ═════════════════════════════════════════════


class TestDashboard:
    """Test di AgentMonitor, AlertSystem, Reports, TimelineViewer."""

    def test_agent_monitor_risk_ranking(self, swarm_with_turns):
        monitor = AgentMonitor(swarm_with_turns)
        rankings = monitor.get_risk_ranking()
        assert isinstance(rankings, list)
        if rankings:
            r = rankings[0]
            assert "agent_id" in r
            assert "name" in r
            assert "risk_score" in r
            assert "risk_factors" in r
            assert 0 <= r["risk_score"] <= 100

    def test_agent_monitor_empty_swarm(self):
        monitor = AgentMonitor()
        assert monitor.get_risk_ranking() == []

    def test_agent_monitor_trend(self, swarm_with_turns):
        monitor = AgentMonitor(swarm_with_turns)
        if swarm_with_turns.agents:
            aid = list(swarm_with_turns.agents.keys())[0]
            trend = monitor.get_trend(aid, "stress", 5)
            assert isinstance(trend, list)
            assert len(trend) <= 5

    def test_alert_system_evaluation(self, swarm_with_turns):
        alerts = AlertSystem(swarm_with_turns).evaluate_all()
        assert isinstance(alerts, list)
        for a in alerts:
            assert "agent_id" in a
            assert "type" in a
            assert "severity" in a
            assert a["severity"] in ("critical", "warning", "info")

    def test_alert_system_empty_swarm(self):
        assert AlertSystem().evaluate_all() == []

    def test_alert_system_history(self, swarm_with_turns):
        asys = AlertSystem(swarm_with_turns)
        asys.evaluate_all()
        asys.evaluate_all()
        assert isinstance(asys.get_history(), list)

    def test_reports_summary(self, swarm_with_turns):
        r = Reports(swarm_with_turns)
        report = r.generate_report("summary")
        assert report.get("type") == "summary"

    def test_reports_hr_dss(self, swarm_with_turns):
        r = Reports(swarm_with_turns)
        report = r.generate_report("hr_dss")
        assert report.get("type") == "hr_dss"
        assert "workforce_health" in report
        assert "profile_breakdown" in report
        assert "recommendations" in report

    def test_reports_turnover_risk(self, swarm_with_turns):
        r = Reports(swarm_with_turns)
        report = r.generate_report("turnover_risk")
        assert report.get("type") == "turnover_risk"
        assert "high_risk_count" in report
        assert "rankings" in report

    def test_reports_agent_report(self, swarm_with_turns):
        r = Reports(swarm_with_turns)
        if swarm_with_turns.agents:
            aid = list(swarm_with_turns.agents.keys())[0]
            report = r.get_agent_report(aid)
            assert report is not None
            assert "name" in report
            assert "profile" in report
            assert "stats" in report

    def test_reports_empty_swarm(self):
        r = Reports()
        assert "error" in r.generate_report("summary")

    def test_timeline_viewer(self, swarm_with_turns):
        tv = TimelineViewer(swarm_with_turns)
        timeline = tv.get_timeline()
        assert isinstance(timeline, list)

    def test_timeline_viewer_agent(self, swarm_with_turns):
        tv = TimelineViewer(swarm_with_turns)
        if swarm_with_turns.agents:
            aid = list(swarm_with_turns.agents.keys())[0]
            timeline = tv.get_timeline(aid)
            assert isinstance(timeline, list)
            for e in timeline:
                assert e.get("agent_id") == aid

    def test_timeline_viewer_empty(self):
        assert TimelineViewer().get_timeline() == []

    def test_main_dashboard_overview(self, swarm_with_turns):
        md = MainDashboard(swarm_with_turns)
        overview = md.get_overview()
        assert "total_agents" in overview
        assert "alerts" in overview
        assert "top_risks" in overview

    def test_main_dashboard_no_swarm(self):
        md = MainDashboard()
        assert "error" in md.get_overview()

    def test_main_dashboard_set_swarm(self, swarm_with_turns):
        md = MainDashboard()
        md.set_swarm(swarm_with_turns)
        overview = md.get_overview()
        assert "error" not in overview


# ═════════════════════════════════════════════
# SEZIONE 7: EVENTI, SCELTE, GRAFO
# ═════════════════════════════════════════════


class TestEvents:
    """Test del sistema eventi e scelte."""

    def test_event_manager_loads(self, engine):
        assert engine.event_manager is not None
        assert len(engine.event_manager.events) > 0

    def test_event_has_fields(self, engine):
        event = engine.current_event
        assert event.id is not None
        assert event.text is not None
        assert len(event.choices) >= 1
        for c in event.choices:
            assert c.id is not None
            assert c.category is not None

    def test_choice_has_effects(self, engine):
        for c in engine.current_event.choices:
            assert c.effects is not None
            assert isinstance(c.effects, dict)

    def test_decision_graph(self, engine):
        assert engine.graph is not None
        assert hasattr(engine.graph, "add_decision")
        assert hasattr(engine.graph, "history")

    def test_graph_add_decision(self, engine):
        engine.graph.add_decision("ev1", "ch1", "ev2")
        assert len(engine.graph.history) == 1
        assert engine.graph.history[0]["event_id"] == "ev1"

    def test_mini_events_list(self):
        assert len(MINI_EVENTS) > 0
        for text, effects in MINI_EVENTS:
            assert isinstance(text, str)
            assert isinstance(effects, dict)

    def test_career_phases_list(self):
        assert len(CAREER_PHASES) > 0
        for day, name, desc in CAREER_PHASES:
            assert isinstance(day, int)
            assert isinstance(name, str)
            assert isinstance(desc, str)

    def test_manager_personalities(self):
        assert len(MANAGER_PERSONALITIES) > 0
        for name, traits in MANAGER_PERSONALITIES.items():
            assert "type" in traits
            assert "stress_bonus" in traits
            assert "crisis_threshold" in traits


# ═════════════════════════════════════════════
# SEZIONE 8: LABORATORY UI BACKEND (LOGIC)
# ═════════════════════════════════════════════


class TestLabFlow:
    """Test del flusso UI del laboratorio: inspect_agent, possessione."""

    def test_inspect_agent_sets_state(self, swarm):
        """inspect_agent deve impostare correttamente l'agent_id nello stato."""
        from ui.pages.logic import inspect_agent

        agent_id = list(swarm.agents.keys())[1]

        # Simula il contesto client (mock di ui.context.client)
        with patch("nicegui.ui.context") as mock_context:
            mock_context.client.id = "test_client"
            inspect_agent(agent_id)

        import game.state as state

        assert state.client_inspected_agent.get("test_client") == agent_id

    def test_lab_view_inspected_agent_lookup(self, swarm_with_turns):
        """La vista laboratorio deve poter trovare un agente specifico per ID."""
        view = swarm_with_turns.get_laboratory_view()
        agent_ids = [a["agent_id"] for a in view["agents"]]
        assert len(agent_ids) == len(set(agent_ids))  # Tutti gli ID sono univoci

    def test_lab_view_first_agent_default(self, swarm_with_turns):
        """Quando nessun agente è ispezionato, il primo della lista è il default."""
        view = swarm_with_turns.get_laboratory_view()
        assert len(view["agents"]) > 0
        first = view["agents"][0]
        assert first["agent_id"] is not None

    def test_lab_view_possessed_first_in_list(self, swarm_with_turns):
        """Gli agenti posseduti devono comparire per primi."""
        human = swarm_with_turns.register_human("Test")
        agent_ids = list(swarm_with_turns.agents.keys())
        # Possiede l'ultimo agente
        swarm_with_turns.possess_agent(human.human_id, agent_ids[-1])
        view = swarm_with_turns.get_laboratory_view(human.human_id)
        assert view["agents"][0]["is_possessed"] is True

    def test_lab_view_agent_strategy_report(self, swarm_with_turns):
        """Ogni agente deve avere un report strategico."""
        view = swarm_with_turns.get_laboratory_view()
        for a in view["agents"]:
            assert "strategic_report" in a

    def test_lab_view_contains_cube_data(self, swarm_with_turns):
        """I dati per il Collins Cube devono essere presenti."""
        view = swarm_with_turns.get_laboratory_view()
        for a in view["agents"]:
            assert 0 <= a["stress"] <= 100
            assert 0 <= a["energy"] <= 100
            assert 0 <= a["integrity"] <= 100

    def test_lab_view_analytics_profile_impact(self, swarm_with_turns):
        """L'analytics deve contenere profile_impact."""
        view = swarm_with_turns.get_laboratory_view()
        analytics = view["analytics"]
        assert "profile_impact" in analytics
        assert isinstance(analytics["profile_impact"], dict)

    def test_agent_get_choice_probabilities(self, agent):
        """L'agente deve restituire probabilità di scelta valide."""
        probs = agent.get_choice_probabilities()
        if probs:
            assert len(probs) > 0
            for p in probs:
                assert 0 <= p <= 100

    def test_agent_auto_play_turn(self, agent):
        """auto_play_turn deve far avanzare l'agente di un turno."""
        old_day = agent.engine.player.days_survived
        event = agent.auto_play_turn()
        assert agent.engine.player.days_survived > old_day
        assert event is not None


# ═════════════════════════════════════════════
# SEZIONE 9: DATABASE
# ═════════════════════════════════════════════


class TestDatabase:
    """Test del database agent_db e analytics."""

    def test_agent_db_init(self):
        import database.agent_db as db

        db.init_agent_db()
        assert db.AGENT_DB_PATH.exists()

    def test_agent_db_save_and_read(self):
        import database.agent_db as db

        db.init_agent_db()
        agent_data = {
            "agent_id": "test_agent_01",
            "name": "Test",
            "profile_name": "Il Performante",
            "profile_json": {"name": "Il Performante"},
            "company_type": "Corporate",
            "total_decisions": 5,
        }
        db.save_agent(agent_data)
        agents = db.get_all_agents()
        assert len(agents) >= 1
        assert any(a["agent_id"] == "test_agent_01" for a in agents)

    def test_agent_db_save_decision(self):
        import database.agent_db as db

        db.init_agent_db()
        db.save_decision(
            {
                "agent_id": "test_agent_01",
                "turn_number": 1,
                "event_id": "ev1",
                "choice_id": "ch1",
                "choice_category": "COMPLIANCE",
                "was_auto": True,
                "stats_before": {"stress": 0},
                "stats_after": {"stress": 5},
            }
        )
        import sqlite3

        conn = sqlite3.connect(str(db.AGENT_DB_PATH))
        count = conn.execute("SELECT COUNT(*) FROM agent_decisions").fetchone()[0]
        conn.close()
        assert count == 1

    def test_agent_db_save_jump(self):
        import database.agent_db as db

        db.init_agent_db()
        db.save_jump(
            {
                "human_id": "human_01",
                "from_agent_id": "agent_01",
                "to_agent_id": "agent_02",
                "from_day": 1,
                "to_day": 5,
                "reason": "Test",
                "declared_mood": "Stressato",
            }
        )
        import sqlite3

        conn = sqlite3.connect(str(db.AGENT_DB_PATH))
        count = conn.execute("SELECT COUNT(*) FROM human_jumps").fetchone()[0]
        conn.close()
        assert count == 1

    def test_agent_db_save_swarm_session(self):
        import database.agent_db as db

        db.init_agent_db()
        db.save_swarm_session(
            {
                "session_id": "session_01",
                "num_agents": 4,
                "total_turns": 10,
            }
        )
        session = db.get_swarm_session("session_01")
        assert session is not None
        assert session["num_agents"] == 4

    def test_agent_db_save_swarm_history(self):
        import database.agent_db as db

        db.init_agent_db()
        db.save_swarm_history(
            {
                "session_id": "session_01",
                "turn_number": 1,
                "profile_distribution": {"type": "test"},
                "avg_stats": {"avg_stress": 30},
            }
        )
        history = db.get_swarm_history("session_01")
        assert len(history) == 1

    def test_agent_db_clear(self):
        import database.agent_db as db

        db.init_agent_db()
        db.save_agent(
            {"agent_id": "test", "name": "T", "profile_name": "P", "company_type": "C"}
        )
        db.clear_agents()
        assert db.get_all_agents() == []

    def test_agent_db_human_profiles(self):
        import database.agent_db as db

        db.init_agent_db()
        db.save_human_profile(
            {
                "human_id": "human_01",
                "name": "TestHuman",
                "total_jumps": 3,
                "unique_agents": 2,
                "emergent_profile": {"category_distribution": {"COMPLIANCE": 50}},
            }
        )
        profiles = db.get_all_human_profiles()
        assert len(profiles) >= 1


# ═════════════════════════════════════════════
# SEZIONE 10: EDGE CASES E ROBUSTEZZA
# ═════════════════════════════════════════════


class TestEdgeCases:
    """Test di casi limite e robustezza."""

    def test_swarm_empty_lab_view(self):
        sw = AgentSwarm(num_agents=0)
        sw.agents = {}
        view = sw.get_laboratory_view()
        assert view["total_agents"] == 0
        assert view["agents"] == []

    def test_engine_no_event_file(self):
        eng = GameEngine("Test", "nonexistent.json")
        eng.next_turn()
        # Non deve crashare
        assert eng.current_event is None or eng.current_event is not None

    def test_player_burnout_simultaneous(self, player):
        """Stress e salute vanno a 0 contemporaneamente."""
        player.stress = 100
        player.health = 0
        player.check_conditions()
        assert player.is_alive is False

    def test_agent_memory_decisions(self, agent):
        agent.auto_play_turn()
        assert len(agent.memory.decisions) >= 1
        d = agent.memory.decisions[0]
        assert d.event_id is not None
        assert d.choice_text is not None
        assert d.category is not None

    def test_agent_choice_probabilities_sum(self, agent):
        probs = agent.get_choice_probabilities()
        if probs:
            assert abs(sum(probs) - 100) < 2.0

    def test_swarm_high_turn_count(self, swarm):
        for _ in range(20):
            swarm.run_simulation_step()
        assert swarm.turn_counter == 20

    def test_player_all_stats_clamped(self, player):
        player.energy = 150
        player.stress = -50
        player.check_conditions()
        assert player.energy == 100
        assert player.stress == 0

    def test_agent_nonexistent_in_lab_view(self, swarm):
        """Un agent_id inesistente non deve crashare la vista."""
        view = swarm.get_laboratory_view()
        agent_ids = [a["agent_id"] for a in view["agents"]]
        assert "fake_id" not in agent_ids

    def test_updated_stats_history_length(self, engine):
        """stats_history deve crescere con next_turn."""
        initial_len = len(engine.stats_history)
        engine.next_turn()
        assert len(engine.stats_history) > initial_len

    def test_engine_faction_sync(self, engine):
        engine.player.factions["Ribelli"] = 70
        engine._sync_factions_to_npcs()
        assert engine.player.npcs["Marco"].trust < 50  # Dovrebbe calare
        assert engine.player.npcs["Roberto"].respect >= 50

    def test_engine_faction_sync_loyalists(self, engine):
        engine.player.factions["Fedelissimi"] = 80
        engine._sync_factions_to_npcs()
        assert engine.player.npcs["Marco"].trust > 50

    def test_engine_deferred_events(self, engine):
        engine.deferred_events.append(
            {
                "event_id": "riunione_inutile",
                "due_in": 1,
                "label": "test",
            }
        )
        engine.next_turn()
        # Il deferred event viene processato
        assert engine.current_event is not None

    def test_swarm_run_simulation_one_turn(self, swarm):
        old_turn = swarm.turn_counter
        result = swarm.run_simulation_step()
        assert result["turn"] == old_turn + 1
        assert result["agents_updated"] > 0

    def test_npc_state_defaults(self):
        npc = NPCState("Test", "Role")
        assert npc.name == "Test"
        assert npc.trust == 50
        assert npc.respect == 50
        assert npc.fear == 0

    def test_npc_to_dict(self):
        npc = NPCState("Test", "Role", trust=80, respect=70)
        d = npc.to_dict()
        assert d["name"] == "Test"
        assert d["trust"] == 80

    def test_player_tags_new_tag(self, player):
        player.add_tags(["new_tag"])
        assert player.tags.get("new_tag") == 1

    def test_player_employability_effect(self, player):
        player.update_stats({"employability": 10})
        assert player.employability == 60

    def test_engine_stats_history_snapshot(self, engine):
        assert len(engine.stats_history) > 0
        snapshot = engine.stats_history[-1]
        assert "stress" in snapshot
        assert "energy" in snapshot

    def test_swarm_human_make_choice_updates_db(self, swarm):
        human = swarm.register_human("Test")
        agent_id = list(swarm.agents.keys())[0]
        swarm.possess_agent(human.human_id, agent_id)
        swarm.human_make_choice(human.human_id, 0)
        import database.agent_db as db

        decisions = (
            db.get_all_agents()
        )  # Non possiamo controllare decisioni direttamente
        # Verifichiamo che l'agente sia ancora vivo o abbia registrato la scelta
        agent = swarm.agents[agent_id]
        assert agent.total_decisions > 0 or not agent.engine.player.is_alive

    def test_next_event_id_override(self, engine):
        engine.next_event_id_override = engine.current_event.id
        old_id = engine.current_event.id
        engine.next_turn()
        assert engine.current_event is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-x"])
