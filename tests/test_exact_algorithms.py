import unittest
from typing import List
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.median_ranking import MedianRanking
from corankco.algorithms.exact.exactalgorithm import ExactAlgorithm
from corankco.ranking import Ranking


class TestAlgos(unittest.TestCase):

    def setUp(self):
        self.test_time_computation: bool = False
        self.my_algs: List[MedianRanking] = [ExactAlgorithm(optimize=True)]
        self.scoring_scheme_unifying = ScoringScheme.get_unifying_scoring_scheme()

    def test_consensus_same_rankings(self):
        dataset = Dataset([Ranking.from_list([{3}, {2}, {1}])] * 3)
        for alg in self.my_algs:
            consensus = alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{3}, {2}, {1}]))



if __name__ == '__main__':
    unittest.main()
