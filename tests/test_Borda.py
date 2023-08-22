import unittest
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.borda.borda import BordaCount
from corankco.ranking import Ranking


class TestBordaCount(unittest.TestCase):

    def setUp(self):
        self.borda_count = BordaCount()
        self.scoring_scheme_unifying = ScoringScheme.get_unifying_scoring_scheme()
        self.scoring_scheme_induced = ScoringScheme.get_induced_measure_scoring_scheme()


if __name__ == '__main__':
    unittest.main()
