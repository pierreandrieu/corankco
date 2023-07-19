"""
Module that contains the class ExactAlgorithm, which consists in choosing Cplex or PuLP version of the exact algorithm
according to the possibility to import cplex.
"""

from corankco.algorithms.exact.exactalgorithmbase import ExactAlgorithmBase
from corankco.algorithms.exact.exactalgorithmcplex import ExactAlgorithmCplex
from corankco.algorithms.exact.exactalgorithmpulp import ExactAlgorithmPulp
from corankco.scoringscheme import ScoringScheme
from corankco.dataset import Dataset
from corankco.consensus import Consensus


class ExactAlgorithm(ExactAlgorithmBase):
    """
    This class provides a wrapper for exact ranking algorithms. It intelligently selects an appropriate exact algorithm
    depending on the availability of the Cplex library. If Cplex is not installed, the class defaults to a free solver.

    The complexity of this algorithm is exponential. In practical use cases, it is expected to execute within a few
    seconds for ranking tasks involving fewer than 80 elements. For larger sets of elements, the performance will be
    significantly influenced by specific characteristics of the input rankings.

    Particularly, if the size of the largest strongly connected component (as described in the research paper
    "Efficient, robust, and effective rank aggregation for massive biological datasets"
    (https://www.researchgate.net/publication/352277711_Efficient_robust_and_effective_rank_aggregation_for_massive_biological_datasets))
    exceeds 100, the algorithm may not complete in a reasonable timeframe or may require excessive memory.
    This information can be determined using ParConsPartition class.
    """

    def __init__(self, optimize=True):
        """
        Initialize the exact algorithm.

        :param optimize: Boolean for whether to optimize the algorithm or not by adding constraints thanks tu sufficient
        conditions. Defaults to True.
        """
        super().__init__(optimize)
        try:
            self._alg = ExactAlgorithmCplex(optimize=optimize)
        except ModuleNotFoundError:
            self._alg = ExactAlgorithmPulp()
        except ImportError:
            self._alg = ExactAlgorithmPulp()

    def compute_consensus_rankings(self, dataset: Dataset, scoring_scheme: ScoringScheme,
                                   return_at_most_one_ranking: bool = True, bench_mode: bool = False) -> Consensus:
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
        return self._alg.compute_consensus_rankings(dataset, scoring_scheme, return_at_most_one_ranking, bench_mode)

    def get_full_name(self) -> str:
        """

        :return: The name of the algorithm, depends on which has been used between Cplex and PULP
        """
        return self._alg.get_full_name()

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme):
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True as ExactAlgorithmCplex can handle any ScoringScheme
        :rtype: bool
        """
        return self._alg.is_scoring_scheme_relevant_when_incomplete_rankings(scoring_scheme)
