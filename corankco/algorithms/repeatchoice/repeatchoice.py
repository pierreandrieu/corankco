from random import shuffle
from numpy import zeros, argmax
from functools import cmp_to_key

from corankco.algorithms.median_ranking import MedianRanking, ScoringSchemeNotHandledException
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature


class RepeatChoice(MedianRanking):

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking=False,
            bench_mode=False
    ) -> Consensus:
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The penalty vectors to consider
        :type scoring_scheme: ScoringScheme (class ScoringScheme in package 'distances')
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :param bench_mode: is bench mode activated. If False, the algorithm may return more information
        :type bench_mode: bool
        :return one or more rankings if the underlying algorithm can find several equivalent consensus rankings
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found.
        In all scenario, the algorithm returns a list of consensus rankings
        :raise ScoringSchemeNotHandledException when the algorithm cannot compute the consensus because the
        implementation of the algorithm does not fit with the scoring scheme
        """

        if not dataset.is_complete and not self.is_scoring_scheme_relevant_when_incomplete_rankings(scoring_scheme):
            raise ScoringSchemeNotHandledException

        if scoring_scheme.is_equivalent_to([[0, 1, 1, 0, 1, 1], [1, 1, 0, 1, 1, 0]]):
            rankings_to_use = dataset.unified_rankings()
        else:
            rankings_to_use = dataset.rankings

        nb_rankings = len(rankings_to_use)
        rankings_copy = list(rankings_to_use)
        shuffle(rankings_copy)
        h = {}
        id_ranking = 0
        for ranking in rankings_copy:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    if element not in h:
                        h[element] = zeros(nb_rankings, dtype=int) - 1
                    h[element][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1

        res = []
        for el in sorted(h.items(), key=cmp_to_key(RepeatChoice.__compare)):
            res.append([el[0]])

        # kem = KemenyComputingFactory(scoring_scheme=self.scoring_scheme)
        # kem = KendallTauGeneralizedNlogN()
        return Consensus(consensus_rankings=[res],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={
                             ConsensusFeature.AssociatedAlgorithm: self.get_full_name()
                         }
                         )

    @staticmethod
    def __compare(e1: tuple, e2: tuple) -> int:
        first_ind_array_e1_inf_array_e2 = argmax(e1[1] < e2[1])
        first_ind_array_e2_inf_array_e1 = argmax(e2[1] < e1[1])
        if first_ind_array_e1_inf_array_e2 < first_ind_array_e2_inf_array_e1:
            return -1
        elif first_ind_array_e2_inf_array_e1 < first_ind_array_e1_inf_array_e2:
            return 1
        return 0

    def get_full_name(self) -> str:
        return "RepeatChoice"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        return scoring_scheme.is_equivalent_to(ScoringScheme.get_induced_measure_scoring_scheme().penalty_vectors) or \
               scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme().penalty_vectors) or \
               scoring_scheme.is_equivalent_to(ScoringScheme.get_induced_measure_scoring_scheme_p(0.5).penalty_vectors)\
               or scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme_p(0.5).penalty_vectors)
