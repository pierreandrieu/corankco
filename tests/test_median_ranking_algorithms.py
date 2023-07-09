import unittest
from typing import List
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.copeland.copeland import CopelandMethod
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.bioconsert.bioco import BioCo
from corankco.algorithms.kwiksort.kwiksortrandom import KwikSortRandom
from corankco.algorithms.borda.borda import BordaCount
from corankco.algorithms.parcons.parcons import ParCons
from corankco.algorithms.median_ranking import MedianRanking
from corankco.algorithms.exact.exactalgorithmgeneric import ExactAlgorithmGeneric
from corankco.algorithms.exact.exactalgorithm import ExactAlgorithm
from corankco.ranking import Ranking
import time


class TestAlgos(unittest.TestCase):

    def setUp(self):
        self.test_time_computation: bool = False
        self.my_algs: List[MedianRanking] = [CopelandMethod(), BordaCount(), BioConsert(), BioCo(), KwikSortRandom()]
        self.my_algs.extend([ParCons(), ExactAlgorithmGeneric(), ExactAlgorithm(optimize=False), ExactAlgorithm(optimize=True)])
        self.scoring_scheme_unifying = ScoringScheme.get_unifying_scoring_scheme()
        self.scoring_scheme_induced = ScoringScheme.get_induced_measure_scoring_scheme()
        self.scoring_scheme_pseudo = ScoringScheme.get_pseudodistance_scoring_scheme()

    def test_consensus_same_rankings(self):
        dataset = Dataset([Ranking.from_list([{3}, {2}, {1}])] * 3)
        for alg in self.my_algs:
            consensus = alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{3}, {2}, {1}]))

    def test_consensus_different_rankings(self):
        dataset = Dataset([Ranking.from_list([{1}, {2}, {3}])] * 1 + [Ranking.from_list([{3}, {2}, {1}])] * 3)
        for alg in self.my_algs:
            consensus = alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{3}, {2}, {1}]))

    def test_consensus_different_rankings_incomplete(self):
        dataset = Dataset([Ranking.from_list([{1}, {2}])] * 3 + [Ranking.from_list([{3}, {2}, {1}])])

        for alg in self.my_algs:
            consensus = alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{1}, {2}, {3}]))
            consensus = alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{1}, {2}, {3}]))
            consensus = alg.compute_consensus_rankings(dataset, self.scoring_scheme_induced)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{3}, {1}, {2}]))

    def test_consensus_different_rankings_incomplete_with_output_ties(self):
        dataset = Dataset([Ranking.from_list([{4, 5}, {2, 3, 1}])] * 3 + [Ranking.from_list([{3}, {2}, {1, 4}])])
        my_algs: List[MedianRanking] = [ParCons(), ExactAlgorithmGeneric()]
        for alg in my_algs:
            consensus = alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{4, 5}, {2, 3, 1}]))
            consensus = alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{4, 5}, {2, 3, 1}]))
            consensus = alg.compute_consensus_rankings(dataset, self.scoring_scheme_induced)
            self.assertEqual(consensus.consensus_rankings[0], Ranking.from_list([{4, 5}, {2, 3, 1}]))

    def test_scalability(self):
        if self.test_time_computation:
            dataset = Dataset.get_random_dataset_markov(2000, 50, 100, True)
            for alg in self.my_algs:
                debut = time.time()
                alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=self.scoring_scheme_unifying)
                fin = time.time()
                print(str(alg) + " " + str(fin - debut))


if __name__ == '__main__':
    unittest.main()
