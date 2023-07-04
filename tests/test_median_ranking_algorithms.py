import unittest
from typing import List
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.copeland.copeland import CopelandMethod
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.bioconsert.bioco import BioCo
from corankco.algorithms.kwiksort.kwiksortrandom import KwikSortRandom
from corankco.algorithms.borda.borda import BordaCount
from corankco.algorithms.median_ranking import MedianRanking
from corankco.ranking import Ranking


class TestAlgos(unittest.TestCase):

    def setUp(self):
        self.my_algs: List[MedianRanking] = [CopelandMethod(), BordaCount(), BioConsert(), BioCo(), KwikSortRandom()]
        self.scoring_scheme_unifying = ScoringScheme.get_unifying_scoring_scheme()
        self.scoring_scheme_induced = ScoringScheme.get_induced_measure_scoring_scheme()
        self.scoring_scheme_pseudo = ScoringScheme.get_pseudodistance_scoring_scheme()
    def test_consensus_same_rankings(self):
        dataset = Dataset([Ranking.from_list([{1}, {2}, {3}])] * 3)
        for alg in self.my_algs:
            print(alg)
            print(alg.get_full_name())
            consensus = alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{1}, {2}, {3}]))

    def test_consensus_different_rankings(self):
        dataset = Dataset([Ranking.from_list([{1}, {2}, {3}])] * 2 + [Ranking.from_list([{3}, {2}, {1}])])
        for alg in self.my_algs:
            consensus = alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{1}, {2}, {3}]))

    def test_consensus_different_rankings_incomplete(self):
        dataset = Dataset([Ranking.from_list([{1}, {2}])] * 3 + [Ranking.from_list([{3}, {2}, {1}])])

        for alg in self.my_algs:
            consensus = alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{1}, {2}, {3}]))
            consensus = alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{1}, {2}, {3}]))
            consensus = alg.compute_consensus_rankings(dataset, self.scoring_scheme_induced)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{3}, {1}, {2}]))


if __name__ == '__main__':
    unittest.main()
