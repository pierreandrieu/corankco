"""
Module containing an abstract class for Exact Algorithm.
"""

from abc import ABC, abstractmethod
from corankco.dataset import Dataset
from corankco.consensus import Consensus
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm


class IncompatibleArgumentsException(Exception):
    """
    Custom exception, to warn the user that the "optimize" parameter can not be True
    if the user wants all the optimal consensuses.
    """


class ExactAlgorithmBase(ABC, RankAggAlgorithm):
    """
    An abstract base class for exact algorithms. This class outlines the interface that all exact algorithms must
    implement.
    """

    def __init__(self, optimize: bool = True):
        """
        Initialize the exact algorithm.

        :param optimize: Boolean for whether to use the graph-based preprocess of ParCons algorithm. Defaults to True.
        WARNING: if optimize = True, then, we cannot ensure that all the optimal consensus will be returned
        """
        self._optimize: bool = optimize

    @abstractmethod
    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking=True,
            bench_mode=False
    ) -> Consensus:
        """
        Abstract method to compute consensus rankings.

        :param dataset: A dataset containing the rankings to aggregate.
        :param scoring_scheme: The penalty vectors to consider.
        :param return_at_most_one_ranking: The algorithm should not return more than one ranking.
        :param bench_mode: Is bench mode activated. If False, the algorithm may return more information.
        :return: One or more consensus rankings.
        """

    @abstractmethod
    def get_full_name(self) -> str:
        """
        Abstract method to get the full name of the algorithm.

        :return: The full name of the algorithm as a string.
        """

    @abstractmethod
    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Abstract method to check if the scoring scheme is relevant when rankings are incomplete.

        :param scoring_scheme: The scoring scheme to check.
        :return: True if the scoring scheme is relevant, False otherwise.
        """
