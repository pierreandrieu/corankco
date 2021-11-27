from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus
from time import time


class ScoringSchemeNotHandledException(Exception):
    pass


class MedianRanking:
    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking: bool = False,
            bench_mode: bool = False
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
        :return Consensus containing a list of rankings. If the algorithm is not able to provide multiple consensus,
        or if return_at_most_one_ranking is True, a Consensus containing a single consensus ranking is returned.
        :raise ScoringSchemeNotHandledException when the algorithm cannot compute the consensus because the
        implementation of the algorithm does not fit with the scoring scheme
        """

        raise NotImplementedError("The method not implemented")

    def get_full_name(self) -> str:
        raise NotImplementedError("The method not implemented")

    def bench_time_consensus(self,
                             dataset: Dataset,
                             scoring_scheme: ScoringScheme,
                             return_at_most_one_ranking: bool = False,
                             lower_bound_time: int = 2) -> float:
        sum_time = 0
        nb_computation = 0
        while sum_time <= lower_bound_time:
            begin = time()
            self.compute_consensus_rankings(dataset, scoring_scheme, return_at_most_one_ranking, True)
            end = time()
            sum_time += end - begin
            nb_computation += 1
        return sum_time / nb_computation

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        :return: a list of distances from distance_enumeration
        """
        raise NotImplementedError("The method not implemented")

    def __repr__(self):
        return self.__class__.__name__ + " " + str(self.__dict__)
