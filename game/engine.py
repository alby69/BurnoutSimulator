from .player import Player
from .events import EventManager, Event, Choice
from .graph import DecisionGraph
from .save_manager import SaveManager
import random

MINI_EVENTS = [
    ("Trovi traffico, arrivi in ufficio già stressato.", {"stress": 3, "energy": -2}),
    (
        "Un collega ti offre un caffè e due parole di incoraggiamento.",
        {"energy": 3, "stress": -2},
    ),
    (
        "Ricevi una notifica da un headhunter su LinkedIn.",
        {"employability": 5, "self_esteem": 3},
    ),
    (
        "La macchinetta del caffè è rotta. Mattinata storta.",
        {"energy": -3, "stress": 2},
    ),
    (
        "Un gatto randagio entra in ufficio e tutti si fermano 5 minuti.",
        {"stress": -3, "energy": 2},
    ),
    (
        "Il PC si blocca proprio mentre stavi salvando il file.",
        {"stress": 4, "energy": -1},
    ),
    (
        "Trovi un biglietto anonimo positivo sulla scrivania.",
        {"self_esteem": 5, "stress": -2},
    ),
    ("L'ascensore è guasto, fai 8 piani a piedi.", {"energy": -2, "health": 1}),
    ("Il riscaldamento è rotto, si lavora col cappotto.", {"stress": 3, "energy": -3}),
    ("Una riunione viene cancellata all'ultimo minuto.", {"stress": -3, "energy": 1}),
    (
        "Oggi è il compleanno di un collega, c'è torta in ufficio.",
        {"stress": -3, "self_esteem": 2},
    ),
    (
        "La connessione internet è lentissima tutto il giorno.",
        {"stress": 4, "energy": -2},
    ),
    (
        "Trovi un parcheggio sotto ufficio, giornata comincia bene.",
        {"stress": -2, "energy": 1},
    ),
    (
        "Il manager ti manda una mail alle 7:30 del mattino.",
        {"stress": 3, "self_esteem": -2},
    ),
    (
        "La pausa pranzo si allunga perché si discute di film.",
        {"energy": 2, "stress": -2},
    ),
]

NPC_FACTION_MAP = {
    "Marco": "Fedelissimi",
    "Giulia": "Fedelissimi",
    "Roberto": "Gruppo Silenzioso",
    "Elena": "Gruppo Silenzioso",
}

MANAGER_PERSONALITIES = {
    "Micromanager Iperattivo": {
        "type": "Micromanager Iperattivo",
        "description": "Risponde ai messaggi alle 2 di notte, vuole update ogni ora, confonde urgenza con produttività.",
        "tone": "frenetico",
        "stress_bonus": 2,
        "rep_bonus_compliance": 3,
        "crisis_threshold": 70,
        "machiavellianism": 40,
        "psychopathy": 20,
        "narcissism": 50
    },
    "Narcisista Burocratico": {
        "type": "Narcisista Burocratico",
        "description": "Prende merito per il lavoro altrui, adora le riunioni inutili, ti valuta sulla visibilità politica.",
        "tone": "manipolativo",
        "stress_bonus": 1,
        "rep_bonus_compliance": 2,
        "crisis_threshold": 50,
        "machiavellianism": 70,
        "psychopathy": 40,
        "narcissism": 90
    },
    "Padre/Padrone Paternalista": {
        "type": "Padre/Padrone Paternalista",
        "description": "Ti tratta come 'uno di famiglia' finché non contraddici il parente del capo.",
        "tone": "paternalista",
        "stress_bonus": 0,
        "rep_bonus_compliance": 4,
        "crisis_threshold": 40,
        "machiavellianism": 60,
        "psychopathy": 30,
        "narcissism": 60
    },
    "Perfezionista Senza Tregua": {
        "type": "Perfezionista Senza Tregua",
        "description": "Niente è mai abbastanza buono. I KPI si alzano ogni trimestre. Le 60h settimanali sono la norma.",
        "tone": "implacabile",
        "stress_bonus": 3,
        "rep_bonus_compliance": 1,
        "crisis_threshold": 80,
        "machiavellianism": 50,
        "psychopathy": 60,
        "narcissism": 40
    },
}

CAREER_PHASES = [
    (0, "Periodo di Prova", "Sei sotto osservazione. Ogni mossa è analizzata."),
    (5, "Primo Progetto", "Ti è stato affidato il primo incarico significativo."),
    (
        15,
        "Fase Operativa",
        "La routine si stabilizza. I giochi politici si intensificano.",
    ),
    (30, "Ristrutturazione", "L'azienda annuncia cambiamenti. Tensione alle stelle."),
    (60, "Sopravvivenza", "Sei arrivato fin qui. Ogni giorno è una vittoria."),
]

THRESHOLD_EVENTS = [
    (
        lambda p: p.stress >= 80 and not p.status.startswith("Burnout"),
        "Sei sopraffatto dallo stress. Le mani tremano davanti alla tastiera.",
        {"health": -3, "self_esteem": -2},
    ),
    (
        lambda p: p.energy <= 20,
        "La stanchezza è tale che fai fatica a tenere gli occhi aperti sul monitor.",
        {"stress": 3, "health": -2},
    ),
    (
        lambda p: p.manager_rep <= 20,
        "Senti parlare di te nell'open space. Si vocifera che il manager stia preparando un dossier su di te.",
        {"stress": 4, "self_esteem": -3},
    ),
    (
        lambda p: p.self_esteem <= 20,
        "Ti guardi allo specchio e non riconosci la persona che sei diventato in questo posto.",
        {"stress": 3, "health": -2, "employability": -2},
    ),
    (
        lambda p: p.health <= 25,
        "Il tuo corpo sta cedendo. Mal di testa costante, tensione cervicale, notti insonni.",
        {"energy": -3, "stress": 2},
    ),
    (
        lambda p: p.factions["Ribelli"] >= 70,
        "Un collega di un altro reparto ti cerca: 'Ho saputo cosa hai fatto. Anch'io la penso così. Parliamo?'",
        {"faction_Ribelli": 5, "npc_Roberto_trust": 3},
    ),
    (
        lambda p: p.factions["Fedelissimi"] >= 70,
        "Marco ti convoca per un 'caffè informale'. Vuole proporti un ruolo di maggiore responsabilità... e controllo.",
        {"npc_Marco_trust": 5, "faction_Fedelissimi": 3},
    ),
]


class GameEngine:
    COMPANY_ARCHETYPES = {
        "Startup Caotica": {
            "energy": 80,
            "stress": 20,
            "manager_rep": 60,
            "description": "Overwork, nessun processo, ritmi frenetici.",
            "hidden_vars": {"agility": 80, "stability": 20},
            "manager_personality": "Micromanager Iperattivo",
        },
        "Corporate Tossica": {
            "energy": 100,
            "stress": 10,
            "manager_rep": 50,
            "description": "Politica interna, micromanagement, burocrazia.",
            "hidden_vars": {"agility": 20, "stability": 80},
            "manager_personality": "Narcisista Burocratico",
        },
        "Azienda Familiare": {
            "energy": 100,
            "stress": 5,
            "manager_rep": 40,
            "description": "Nepotismo, favoritismi, dinamiche 'da famiglia'.",
            "hidden_vars": {"loyalty": 90, "merit": 10},
            "manager_personality": "Padre/Padrone Paternalista",
        },
        "Consulting": {
            "energy": 70,
            "stress": 30,
            "manager_rep": 70,
            "description": "KPI ossessivi, disponibilità continua, orientamento al cliente.",
            "hidden_vars": {"pressure": 90, "prestige": 70},
            "manager_personality": "Perfezionista Senza Tregua",
        },
    }

    def __init__(
        self,
        player_name: str,
        events_file: str,
        company_type: str = "Corporate Tossica",
        psych_profile = None,
        hr_params: dict = None
    ):
        self.player = Player(name=player_name, company_type=company_type)
        self.psych_profile = psych_profile
        self.hr_params = hr_params or {}
        self.apply_archetype(company_type)
        self.event_manager = EventManager(events_file)
        self.graph = DecisionGraph()
        self.save_manager = SaveManager()
        self.current_event = None
        self.next_event_id_override = None
        self.history = []
        self.hidden_vars = (
            self.COMPANY_ARCHETYPES[company_type].get("hidden_vars", {}).copy()
        )
        self.hidden_vars["manager_patience"] = 70
        self.hidden_vars["company_crisis"] = 10
        self.current_mini_event = None
        self._last_factions = dict(self.player.factions)
        self.deferred_events = []
        self._tutorial_step = 0
        arch = self.COMPANY_ARCHETYPES.get(
            company_type, self.COMPANY_ARCHETYPES["Corporate Tossica"]
        )
        self.manager_personality = MANAGER_PERSONALITIES.get(
            arch.get("manager_personality", ""), {}
        )
        self.stats_history = [dict(self.player.to_dict()["stats"])]
        self.real_cases_mode = False
        self._last_threshold_triggers = set()

    def apply_archetype(self, archetype_name):
        if archetype_name in self.COMPANY_ARCHETYPES:
            arch = self.COMPANY_ARCHETYPES[archetype_name]
            self.player.energy = arch.get("energy", 100)
            self.player.stress = arch.get("stress", 0)
            self.player.manager_rep = arch.get("manager_rep", 50)

    def next_turn(self):
        self.player.days_survived += 1
        p = self.player

        # Mini-evento giornaliero
        self.current_mini_event = random.choice(MINI_EVENTS)
        p.update_stats(self.current_mini_event[1], manager_traits=self.manager_personality, psych_profile=self.psych_profile, hr_params=self.hr_params)

        # Threshold-triggered events
        self.process_threshold_events()

        # Manager personality passive effect
        mp = self.manager_personality
        if mp and mp.get("stress_bonus", 0) > 0:
            stress_bonus = mp["stress_bonus"]
            if self.psych_profile:
                stress_bonus = self.psych_profile.modulate_stat_change("stress", stress_bonus, mp, self.hr_params)
            p.stress = max(0, min(100, p.stress + stress_bonus))

        # Process deferred events
        deferred_override = None
        for d in self.deferred_events:
            d["due_in"] -= 1
            if d["due_in"] <= 0:
                deferred_override = d["event_id"]
        self.deferred_events = [d for d in self.deferred_events if d["due_in"] > 0]

        if deferred_override:
            self.current_event = self.event_manager.get_event(deferred_override)
        elif self.next_event_id_override:
            self.current_event = self.event_manager.get_event(
                self.next_event_id_override
            )
            self.next_event_id_override = None
        else:
            self.current_event = self.event_manager.get_random_event(
                exclude_ids=self.history[-10:]
            )

        if self.current_event:
            self.history.append(self.current_event.id)

        # Stats history snapshot
        self.stats_history.append(dict(p.to_dict()["stats"]))

        return self.current_event

    def process_threshold_events(self):
        p = self.player
        trigger_key = None
        for condition, text, effects in THRESHOLD_EVENTS:
            if condition(p):
                trigger_key = (text, str(effects))
                if trigger_key not in self._last_threshold_triggers:
                    self._last_threshold_triggers.add(trigger_key)
                    self.current_mini_event = (text, effects)
                    p.update_stats(effects, manager_traits=self.manager_personality, psych_profile=self.psych_profile, hr_params=self.hr_params)
                    return
        self._last_threshold_triggers.clear()

    def get_career_phase(self):
        d = self.player.days_survived
        phase = CAREER_PHASES[0]
        for day, name, desc in reversed(CAREER_PHASES):
            if d >= day:
                phase = (day, name, desc)
                break
        return phase

    def _sync_factions_to_npcs(self):
        p = self.player
        current = dict(p.factions)

        for faction, value in current.items():
            prev = self._last_factions.get(faction, value)
            if value == prev:
                continue
            delta = value - prev

            if faction == "Fedelissimi":
                p.npcs["Marco"].trust = max(
                    0, min(100, p.npcs["Marco"].trust + delta // 5)
                )
                p.npcs["Marco"].respect = max(
                    0, min(100, p.npcs["Marco"].respect + delta // 8)
                )
                p.npcs["Giulia"].trust = max(
                    0, min(100, p.npcs["Giulia"].trust + delta // 6)
                )
                if value > 60:
                    p.npcs["Roberto"].respect = max(
                        0, p.npcs["Roberto"].respect - delta // 10
                    )

            elif faction == "Ribelli":
                p.npcs["Marco"].trust = max(0, p.npcs["Marco"].trust - delta // 4)
                p.npcs["Giulia"].fear = max(
                    0, min(100, p.npcs["Giulia"].fear + delta // 6)
                )
                p.npcs["Roberto"].respect = max(
                    0, min(100, p.npcs["Roberto"].respect + delta // 6)
                )
                p.npcs["Elena"].trust = max(
                    0, min(100, p.npcs["Elena"].trust + delta // 10)
                )

            elif faction == "Gruppo Silenzioso":
                p.npcs["Elena"].trust = max(
                    0, min(100, p.npcs["Elena"].trust + delta // 8)
                )
                p.npcs["Roberto"].trust = max(
                    0, min(100, p.npcs["Roberto"].trust + delta // 10)
                )

        self._last_factions = current

    def handle_choice(self, choice_index: int):
        if not self.current_event or choice_index >= len(self.current_event.choices):
            return False

        choice = self.current_event.choices[choice_index]

        # Update player stats
        self.player.update_stats(choice.effects, manager_traits=self.manager_personality, psych_profile=self.psych_profile, hr_params=self.hr_params)

        # Sincronizza fazioni → NPC
        self._sync_factions_to_npcs()

        if hasattr(choice, "tags") and choice.tags:
            self.player.add_tags(choice.tags)

        self.graph.add_decision(self.current_event.id, choice.id, choice.next_event_id)

        if "manager_patience" in self.hidden_vars:
            mp = self.manager_personality
            resistance_penalty = 5 + (mp.get("stress_bonus", 0) * 2 if mp else 0)
            compliance_bonus = 2 + (mp.get("rep_bonus_compliance", 0) if mp else 0)
            if choice.category == "RESISTANCE":
                self.hidden_vars["manager_patience"] -= resistance_penalty
            elif choice.category == "COMPLIANCE":
                self.hidden_vars["manager_patience"] += compliance_bonus

        if random.random() < 0.1:
            self.hidden_vars["company_crisis"] += 5

        # Deferred consequences
        for con in choice.consequences:
            self.deferred_events.append(
                {
                    "event_id": con["event_id"],
                    "due_in": con["after_turns"],
                    "label": con.get("label", ""),
                }
            )

        if choice.next_event_id:
            if "|" in choice.next_event_id:
                parts = choice.next_event_id.split("|")
                options = parts[1].split(";")
                choices_list = []
                weights = []
                for opt in options:
                    ev_id, weight = opt.split(":")
                    choices_list.append(ev_id)
                    weights.append(int(weight))
                self.next_event_id_override = random.choices(
                    choices_list, weights=weights
                )[0]
            else:
                self.next_event_id_override = choice.next_event_id

        return True

    def is_game_over(self):
        return not self.player.is_alive

    def save_game(self):
        return self.save_manager.save_session(self.player, self.graph)
