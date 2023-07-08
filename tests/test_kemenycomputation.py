import unittest
from corankco.scoringscheme import ScoringScheme
from corankco.dataset import Dataset
from corankco.ranking import Ranking
from corankco.kemeny_score_computation import KemenyComputingFactory
from random import seed


class TestKemenyComputation(unittest.TestCase):
    def setUp(self):
        # Creation of 3 scoring schemes
        self._sc1 = ScoringScheme.get_pseudodistance_scoring_scheme_p(0.5)
        self._sc2 = ScoringScheme.get_induced_measure_scoring_scheme_p(0.5)
        self._sc3 = ScoringScheme.get_unifying_scoring_scheme_p(0.5)

        # Creation of three instances to compute Kemeny scores given a scoring scheme
        self._kemeny1 = KemenyComputingFactory(self._sc1)
        self._kemeny2 = KemenyComputingFactory(self._sc2)
        self._kemeny3 = KemenyComputingFactory(self._sc3)

    def test_kemeny_score(self):
        dataset = Dataset.from_raw_list(([[{1}], [{1}], [{1}]]))
        consensus: Ranking = Ranking.from_list([{1}])
        score: float = self._kemeny1.get_kemeny_score(consensus, dataset)
        self.assertEqual(score, 0.)
        dataset: Dataset = Dataset.from_raw_list(([[{2}, {1}], [{1}, {2}], [{2}, {1}]]))
        consensus: Ranking = Ranking.from_list([{1}, {2}])
        score: float = self._kemeny1.get_kemeny_score(consensus, dataset)
        self.assertEqual(score, 2.)
        self.assertEqual(TestKemenyComputation.naive_score_implementation(consensus, dataset, self._sc1), 2.)

    def test_compare_nlogn_nsquare_scores(self):
        for i in range(100):
            dataset_test = Dataset.get_random_dataset_markov(nb_elem=8, nb_rankings=5, steps=300, complete=False)
            consensus = Ranking.generate_rankings(20, 1, 1000, complete=True)[0]

            # test with sc 1
            score_nlogn = self._kemeny1.get_kemeny_score(consensus, dataset_test)
            score_nsquare = TestKemenyComputation.naive_score_implementation(consensus, dataset_test, self._sc1)
            self.assertEqual(score_nlogn, score_nsquare)

            # test with sc 2
            score_nlogn = self._kemeny2.get_kemeny_score(consensus, dataset_test)
            score_nsquare = TestKemenyComputation.naive_score_implementation(consensus, dataset_test, self._sc2)
            self.assertEqual(score_nlogn, score_nsquare)

            # test with sc 3
            score_nlogn = self._kemeny3.get_kemeny_score(consensus, dataset_test)
            score_nsquare = TestKemenyComputation.naive_score_implementation(consensus, dataset_test, self._sc3)
            self.assertEqual(score_nlogn, score_nsquare)

    @staticmethod
    def naive_score_implementation(consensus: Ranking, dataset: Dataset, sc: ScoringScheme) -> float:
        # the consensus ranking as target for the computation of the score
        r_cons: Ranking = consensus
        # its number of buckets
        nb_buckets_cons = len(r_cons)
        # score of the consensus
        score: float = 0.

        for r_input in dataset:
            # compute score associated to each ranking
            score_ri = 0.
            # pos_r_input[e] = position of e in ranking r_input
            pos_r_input = r_input.positions

            # for each bucket i
            for i in range(nb_buckets_cons):
                bucket_i_cons = r_cons[i]
                # for each bucket j > i, all elements of bucket i are before j : vector b
                for j in range(i+1, nb_buckets_cons):
                    bucket_j_cons = r_cons[j]

                    # for each element of bucket j > i in the target input ranking
                    for elem_i_cons in bucket_i_cons:
                        # get the position of elements i and j in the target input ranking, -1 if non-ranked
                        if elem_i_cons in pos_r_input:
                            pos_i_r_input = pos_r_input[elem_i_cons]
                        else:
                            pos_i_r_input = -1

                        for elem_j_cons in bucket_j_cons:
                            if elem_j_cons in pos_r_input:
                                pos_j_r_input = pos_r_input[elem_j_cons]
                            else:
                                pos_j_r_input = -1

                            # add to score_ri the appropriated value
                            if pos_i_r_input == -1 and pos_j_r_input == -1:
                                score_ri += sc.b6

                            elif pos_i_r_input == -1:
                                score_ri += sc.b5
                            elif pos_j_r_input == -1:
                                score_ri += sc.b4
                            elif pos_i_r_input < pos_j_r_input:
                                score_ri += sc.b1
                            elif pos_i_r_input == pos_j_r_input:
                                score_ri += sc.b3
                            else:
                                score_ri += sc.b2

                # now, for each bucket i, we should consider the pairs of elements in bucket i (tied in the consensus)
                for elem_i_cons in bucket_i_cons:
                    if elem_i_cons in pos_r_input:
                        pos_i_r_input = pos_r_input[elem_i_cons]
                    else:
                        pos_i_r_input = -1
                    for elem_j_cons in bucket_i_cons:
                        # this condition not to count the pairs twice
                        if elem_i_cons < elem_j_cons:
                            if elem_j_cons in pos_r_input:
                                pos_j_r_input = pos_r_input[elem_j_cons]
                            else:
                                pos_j_r_input = -1

                            if pos_i_r_input == -1 and pos_j_r_input == -1:
                                score_ri += sc.t6

                            elif pos_i_r_input == -1 or pos_j_r_input == -1:
                                score_ri += sc.t4_and_t5
                            elif pos_i_r_input == pos_j_r_input:
                                score_ri += sc.t3
                            else:
                                score_ri += sc.t1_and_t2
            score += score_ri
        return score


if __name__ == '__main__':
    unittest.main()
