import unittest
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.ranking import Ranking


class TestBordaCount(unittest.TestCase):

    def setUp(self):
        self.my_alg = BioConsert()
        self.scoring_scheme_unifying = ScoringScheme.get_unifying_scoring_scheme()
        self.scoring_scheme_induced = ScoringScheme.get_induced_measure_scoring_scheme()
        self.scoring_scheme_pseudo = ScoringScheme.get_pseudodistance_scoring_scheme()

    def test_consensus_same_rankings(self):
        dataset = Dataset([Ranking([{1}, {2}, {3}])] * 3)
        consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(str(consensus.consensus_rankings[0]), str(Ranking([{1}, {2}, {3}])))

    def test_consensus_different_rankings(self):
        dataset = Dataset([Ranking([{1}, {2}, {3}])] * 2 + [Ranking([{3}, {2}, {1}])])
        consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(str(consensus.consensus_rankings[0]), str(Ranking([{1}, {2}, {3}])))

    def test_consensus_more_than_one(self):
        dataset = Dataset([Ranking([{1}, {2}])] + [Ranking([{2}, {1}])])

        consensus = self.my_alg.compute_consensus_rankings(dataset, ScoringScheme.get_pseudodistance_scoring_scheme_p(1.), False)
        self.assertEqual(len(consensus), 2)

        consensus = self.my_alg.compute_consensus_rankings(dataset,
                                                           ScoringScheme.get_pseudodistance_scoring_scheme_p(0.5), False)
        self.assertEqual(len(consensus), 3)


    def test_consensus_different_rankings(self):
        dataset = Dataset([Ranking([{1}, {2}, {3}])] * 2 + [Ranking([{3}, {2}, {1}])])
        consensus = self.my_alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(str(consensus.consensus_rankings[0]), str(Ranking([{1}, {2}, {3}])))

if __name__ == '__main__':
    unittest.main()
