import unittest
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.bioconsert.bioco import BioCo
from corankco.ranking import Ranking
from corankco.algorithms.median_ranking import ScoringSchemeNotHandledException


class TestBordaCount(unittest.TestCase):

    def setUp(self):
        self.my_alg = BioCo()
        self.scoring_scheme_unifying = ScoringScheme.get_unifying_scoring_scheme()
        self.scoring_scheme_induced = ScoringScheme.get_induced_measure_scoring_scheme()
        self.scoring_scheme_pseudo = ScoringScheme.get_pseudodistance_scoring_scheme()

    def test_consensus_same_rankings(self):
        dataset = Dataset([Ranking.from_list([{1}, {2}, {3}])] * 3)
        consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{1}, {2}, {3}]))

    def test_consensus_different_rankings(self):
        dataset = Dataset([Ranking.from_list([{1}, {2}, {3}])] * 2 + [Ranking.from_list([{3}, {2}, {1}])])
        consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{1}, {2}, {3}]))

    def test_consensus_different_rankings_incomplete(self):
        dataset = Dataset([Ranking.from_list([{1}, {2}])] * 3 + [Ranking.from_list([{3}, {2}, {1}])])

        consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{1}, {2}, {3}]))

        consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_induced)
        self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{3}, {1}, {2}]))

        with self.assertRaises(ScoringSchemeNotHandledException):
            consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_pseudo)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{3}, {1}, {2}]))

if __name__ == '__main__':
    unittest.main()
