import unittest
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.copeland.copeland import CopelandMethod
from corankco.ranking import Ranking
from corankco.consensus import ConsensusFeature


class TestCopeland(unittest.TestCase):

    def setUp(self):
        self.my_alg = CopelandMethod()
        self.scoring_scheme_unifying = ScoringScheme.get_unifying_scoring_scheme()
        self.scoring_scheme_induced = ScoringScheme.get_induced_measure_scoring_scheme()
        self.scoring_scheme_pseudo = ScoringScheme.get_pseudodistance_scoring_scheme()

    def test_consensus_different_rankings_incomplete(self):
        dataset = Dataset([Ranking([{1}, {2}])] * 3 + [Ranking([{3}, {2}, {1}])])

        consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(consensus.consensus_rankings[0], Ranking([{1}, {2}, {3}]))
        self.assertEqual(consensus.features[ConsensusFeature.COPELAND_SCORES], {1: 2, 2: 1, 3: 0})
        consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_induced)
        self.assertEqual(consensus.consensus_rankings[0], Ranking([{3}, {1}, {2}]))


if __name__ == '__main__':
    unittest.main()
