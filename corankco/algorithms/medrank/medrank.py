from itertools import zip_longest

from corankco.algorithms.median_ranking import MedianRanking, ScoringSchemeNotHandledException
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature


class MedRank(MedianRanking):
    def __init__(self,  h=0.5):
        if h < 0:
            h = 0
        elif h > 1:
            h = 1
        self.__h = h

    # Complexity : 0 (2 * n) with adaptation for induced measure
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

        if scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme().penalty_vectors) or \
                scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme_p(0.5).penalty_vectors):
            rankings_to_use = dataset.unified_rankings()
        else:
            rankings_to_use = dataset.rankings
        has = {}

        nb_rankings_needed = {}
        already_put = set()

        for ranking in rankings_to_use:
            for bucket in ranking:
                for element in bucket:
                    if element not in nb_rankings_needed:
                        nb_rankings_needed[element] = self.__h
                    else:
                        nb_rankings_needed[element] += self.__h

        bucket_res = []
        ranking_res = []

        for reorganized in zip_longest(*rankings_to_use):
            for bucket in reorganized:
                if bucket is not None:
                    for element in bucket:
                        if element not in already_put:
                            if element not in has:
                                has[element] = 1
                                if nb_rankings_needed[element] <= 1:
                                    bucket_res.append(element)
                                    already_put.add(element)
                            else:
                                has[element] += 1
                                if has[element] >= nb_rankings_needed[element]:
                                    bucket_res.append(element)
                                    already_put.add(element)
            if len(bucket_res) > 0:
                ranking_res.append(bucket_res)
                bucket_res = []

        rankings_consensus = [ranking_res] if len(ranking_res) > 0 else [[]]
        return Consensus(consensus_rankings=rankings_consensus,
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={
                              ConsensusFeature.AssociatedAlgorithm: self.get_full_name()
                              }
                         )

    def get_full_name(self) -> str:
        return "MedRank"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        return scoring_scheme.is_equivalent_to(ScoringScheme.get_induced_measure_scoring_scheme().penalty_vectors) or \
               scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme().penalty_vectors) or \
               scoring_scheme.is_equivalent_to(ScoringScheme.get_induced_measure_scoring_scheme_p(0.5).penalty_vectors)\
               or scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme_p(0.5).penalty_vectors)
