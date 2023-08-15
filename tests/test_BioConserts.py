import unittest
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.bioconsert.BioConsertPythonFast import BioConsertPythonFast
from corankco.ranking import Ranking
import time
from random import seed
from numpy.random import seed as np_seed
import cProfile
import pstats


class TestBioConserts(unittest.TestCase):

    def setUp(self):
        self.my_alg1 = BioConsertPythonFast()

        self.scoring_scheme_unifying = ScoringScheme.get_unifying_scoring_scheme()
        self.scoring_scheme_induced = ScoringScheme.get_induced_measure_scoring_scheme()
        self.scoring_scheme_pseudo = ScoringScheme.get_pseudodistance_scoring_scheme()

    def test_consensus_same_rankings(self):
        dataset = Dataset([Ranking([{1}, {2}, {3}])] * 3)
        consensus = self.my_alg1.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(str(consensus.consensus_rankings[0]), str(Ranking([{1}, {2}, {3}])))

    def test_consensus_different_rankings(self):
        dataset = Dataset([Ranking([{1}, {2}, {3}])] * 2 + [Ranking([{3}, {2}, {1}])])
        consensus = self.my_alg1.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(str(consensus.consensus_rankings[0]), str(Ranking([{1}, {2}, {3}])))

    def test_consensus_different_rankings_incomplete(self):
        dataset = Dataset([Ranking([{1}, {2}])] * 3 + [Ranking([{3}, {2}, {1}])])

        consensus = self.my_alg1.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)
        self.assertEqual(str(consensus.consensus_rankings[0]), str(Ranking([{1}, {2}, {3}])))

        consensus = self.my_alg1.compute_consensus_rankings(dataset, self.scoring_scheme_induced)
        self.assertEqual(str(consensus.consensus_rankings[0]), str(Ranking([{3}, {1}, {2}])))

    def test_scalability(self):
        seed(1)
        np_seed(1)
        dataset = Dataset.get_random_dataset_markov(1000, 50, 10000, True)
        print("dataset = ")
        alg = self.my_alg1

        # Profilage avec cProfile
        profiler = cProfile.Profile()
        profiler.enable()
        self._compute_consensus(alg, dataset)
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('cumulative')
        stats.print_stats()

        # Mesure du temps d'exécution
        debut = time.time()
        self._compute_consensus(alg, dataset)
        fin = time.time()
        print(str(alg) + " " + str(fin - debut))

    def _compute_consensus(self, alg, dataset):
        alg.compute_consensus_rankings(dataset, self.scoring_scheme_unifying)


if __name__ == '__main__':
    unittest.main()
