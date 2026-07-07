import unittest
from game.ending_resolver import resolver
from game.player import Player
from game.models import CompanyArchetype

class MockPlayer:
    def __init__(self, **kwargs):
        self.factions = kwargs.get('factions', {"Ribelli": 0, "Fedelissimi": 0, "Gruppo Silenzioso": 0})
        self.integrity = kwargs.get('integrity', 50)
        self.manager_rep = kwargs.get('manager_rep', 50)
        self.company_type = kwargs.get('company_type', CompanyArchetype.CORPORATE)
        self.tags = kwargs.get('tags', {})
        self.energy = kwargs.get('energy', 50)
        self.days_survived = kwargs.get('days_survived', 0)
        self.self_esteem = kwargs.get('self_esteem', 50)
        self.is_alive = kwargs.get('is_alive', True)
        self.status = kwargs.get('status', 'Attivo')

class TestEndingResolver(unittest.TestCase):
    def test_whistleblower(self):
        p = MockPlayer(factions={"Ribelli": 75}, integrity=70)
        self.assertEqual(resolver.resolve(p), "IL WHISTLEBLOWER")

    def test_braccio_destro(self):
        p = MockPlayer(factions={"Fedelissimi": 75}, manager_rep=85)
        self.assertEqual(resolver.resolve(p), "IL BRACCIO DESTRO")

    def test_martire(self):
        p = MockPlayer(integrity=85, manager_rep=20)
        self.assertEqual(resolver.resolve(p), "IL MARTIRE")

    def test_burnout_ending(self):
        p = MockPlayer(status="Burnout Severo")
        self.assertEqual(resolver.resolve(p), "IL CADUTO")

    def test_startup_burnout(self):
        p = MockPlayer(company_type=CompanyArchetype.STARTUP, tags={"burnout_risk": 6})
        self.assertEqual(resolver.resolve(p), "IL FONDATORE ESAURITO")

if __name__ == "__main__":
    unittest.main()
