"""
Module that contains an abstract class to define the functions to be implemented for a rank aggregation algorithm.
"""

from time import time
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus


class ScoringSchemeNotHandledException(Exception):
    """
    Custom exception, when the scoring scheme cannot be used with the chosen algorithm given the dataset.
    Note that this exception cannot be raised if the dataset is complete.
    """


class RankAggAlgorithm:

    """
    The RankAggAlgorithm class serves as an interface for implementing consensus ranking algorithms. It defines
    several methods that each consensus ranking algorithm should implement, including the computation of
    consensus rankings, determining whether a given scoring scheme is relevant for incomplete rankings,
    and benchmarking the consensus computation time. An algorithm implemented using this interface should
    also provide a full name and a string representation of itself.
    """
    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking: bool = True,
            bench_mode: bool = False
    ) -> Consensus:
        """
        Calculate and return the consensus rankings based on the given dataset and scoring scheme.

        :param dataset: The dataset of rankings to be aggregated.
        :type dataset: Dataset
        :param scoring_scheme: The scoring scheme to be used for calculating consensus.
        :type scoring_scheme: ScoringScheme
        :param return_at_most_one_ranking: If True, the algorithm should return at most one ranking.
        :type return_at_most_one_ranking: bool
        :param bench_mode: If True, the algorithm may return additional information for benchmarking purposes.
        :type bench_mode: bool
        :return: Consensus rankings. If the algorithm is unable to provide multiple consensuses or
        return_at_most_one_ranking is True, a single consensus ranking is returned.
        :rtype: Consensus
        :raise ScoringSchemeNotHandledException: When the algorithm cannot compute the consensus because the
        implementation does not support the given scoring scheme.
        """
        raise NotImplementedError("The method not implemented")

    def get_full_name(self) -> str:
        """
        Get the full name of the algorithm.

        :return: The full name of the algorithm.
        :rtype: str
        """
        raise NotImplementedError("The method not implemented")

    def bench_time_consensus(self,
                             dataset: Dataset,
                             scoring_scheme: ScoringScheme,
                             return_at_most_one_ranking: bool = True,
                             lower_bound_time: float = 1.) -> float:
        """
        Calculate and return the average computation time for a given dataset and scoring scheme

        :param dataset: The dataset of rankings to be aggregated.
        :type dataset: Dataset
        :param scoring_scheme: The scoring scheme to be used for calculating consensus.
        :type scoring_scheme: ScoringScheme
        :param return_at_most_one_ranking: If True, the algorithm should return at most one ranking.
        :type return_at_most_one_ranking: bool
        :param lower_bound_time: The lower bound on the total computation time.
        :type lower_bound_time: float
        :return: The average computation time.
        :rtype: float
        """
        sum_time: float = 0
        nb_computation: int = 0
        while sum_time <= lower_bound_time:
            begin = time()
            self.compute_consensus_rankings(
                dataset, scoring_scheme, return_at_most_one_ranking, True)
            end = time()
            sum_time += end - begin
            nb_computation += 1
        return sum_time / nb_computation

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Determine whether the provided scoring scheme is relevant when dealing with incomplete rankings.

        :param scoring_scheme: The scoring scheme to be evaluated.
        :type scoring_scheme: ScoringScheme
        :return: True if the scoring scheme is relevant for incomplete rankings, False otherwise.
        :rtype: bool
        """
        raise NotImplementedError("The method not implemented")

    def __repr__(self):
        """
        Return a string representation of the object, including the class name and all instance variables.
        The instance variables can be specific parameters for a given MedianRanking algorithm

        :return: A string representation of the object.
        :rtype: str
        """
        return self.__class__.__name__ + " " + str(self.__dict__)
