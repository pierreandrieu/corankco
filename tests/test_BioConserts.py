import unittest
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.bioconsert.BioConsertPythonFast import BioConsertPythonFast
from corankco.ranking import Ranking
import time

class TestBioConserts(unittest.TestCase):

    def setUp(self):
        self.my_alg1 = BioConsertPythonFast()
        self.my_alg2 = BioConsert()

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
        algs = [self.my_alg1, self.my_alg2]
        for nb_elem in range(10, 101, 10):
            print("nb_elem = ", nb_elem)
            dataset = Dataset.get_random_dataset_markov(nb_elem, 20, nb_elem * 10, True)
            for alg in algs:
                if "onsert" in alg.get_full_name():
                    debut = time.time()
                    alg.compute_consensus_rankings(dataset=dataset, scoring_scheme=self.scoring_scheme_unifying)
                    fin = time.time()
                    print(str(alg) + " " + str(fin - debut))

if __name__ == '__main__':
    unittest.main()
