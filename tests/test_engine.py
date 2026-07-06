import unittest
import os
from game.engine import GameEngine, CompanyArchetype
from game.models import PlayerState

class TestGameEngine(unittest.TestCase):
    def setUp(self):
        # Ensure we have a valid events file for testing
        self.events_file = "game/data/events.json"

    def test_engine_init(self):
        engine = GameEngine("Test Player", self.events_file, CompanyArchetype.STARTUP.value)
        self.assertEqual(engine.player.name, "Test Player")
        self.assertEqual(engine.player.company_type, CompanyArchetype.STARTUP)
        # Check initial stats from archetype
        self.assertEqual(engine.player.energy, 80)
        self.assertEqual(engine.player.stress, 20)

    def test_handle_choice(self):
        engine = GameEngine("Test Player", self.events_file)
        event = engine.next_turn()
        self.assertIsNotNone(event)

        initial_stress = engine.player.stress
        # Assume first choice exists and is valid
        success = engine.handle_choice(0)
        self.assertTrue(success)
        # History should have the event
        self.assertEqual(len(engine.history), 1)

    def test_career_phases(self):
        engine = GameEngine("Test Player", self.events_file)
        engine.player.days_survived = 0
        self.assertEqual(engine.get_career_phase()[1], "Periodo di Prova")

        engine.player.days_survived = 35
        self.assertEqual(engine.get_career_phase()[1], "Ristrutturazione")

    def test_game_over(self):
        engine = GameEngine("Test Player", self.events_file)
        engine.player.health = 0
        engine.player.is_alive = False
        self.assertTrue(engine.is_game_over())

if __name__ == "__main__":
    unittest.main()
