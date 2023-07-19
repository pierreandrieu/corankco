"""
Module that allows to select an algorithm using an enumeration, with the parameters of the algorithm.
"""

from enum import Enum, unique
from typing import Dict, List
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.parcons.parcons import ParCons
from corankco.algorithms.exact.exactalgorithm import ExactAlgorithm
from corankco.algorithms.kwiksort.kwiksortrandom import KwikSortRandom
from corankco.algorithms.pickaperm.pickaperm import PickAPerm
from corankco.algorithms.borda.borda import BordaCount
from corankco.algorithms.bioconsert.bioco import BioCo
from corankco.algorithms.copeland.copeland import CopelandMethod


class AlgorithmEnumeration:
    """Contains a list of classes for all available ranking algorithms."""
    median_ranking_algorithms = [
        ExactAlgorithm,
        ParCons,
        BioConsert,
        BioCo,
        KwikSortRandom,
        BordaCount,
        CopelandMethod,
        PickAPerm,
    ]


@unique
class Algorithm(Enum):
    """Enum representing the available ranking algorithms."""
    EXACT = 0
    PARCONS = 1
    BIOCONSERT = 2
    BIOCO = 3
    KWIKSORTRANDOM = 4
    PICKAPERM = 5
    BORDACOUNT = 6
    COPELANDMETHOD = 7

    @staticmethod
    def get_all() -> List['Algorithm']:
        """
        Returns a list of all available algorithms.

        :return: A List of all the available algorithms.
        :rtype: List[Algorithm]
        """
        return [Algorithm.EXACT, Algorithm.PARCONS, Algorithm.BIOCONSERT, Algorithm.BIOCO, Algorithm.KWIKSORTRANDOM,
                Algorithm.PICKAPERM, Algorithm.BORDACOUNT, Algorithm.COPELANDMETHOD]

    @staticmethod
    def get_all_compatible_with_any_scoring_scheme() -> List['Algorithm']:
        """
        Returns a list of algorithms that are compatible with any scoring scheme.

        The returned algorithms have implementations that can handle any scoring scheme.

        :return: A List of all the algorithms compatible with any scoring scheme.
        :rtype: List[Algorithm]
        """
        return [Algorithm.EXACT, Algorithm.PARCONS, Algorithm.BIOCONSERT,
                Algorithm.KWIKSORTRANDOM, Algorithm.COPELANDMETHOD]


def get_algorithm(alg: Algorithm, parameters: Dict = None) -> RankAggAlgorithm:
    """
    Returns an instance of the specified algorithm.

    :param alg: The algorithm to instantiate. Must be an instance of the Algorithm enum.
    :type alg: Algorithm
    :param parameters: The parameters to pass to the algorithm's constructor. If None, an empty dict will be used.
    :type parameters: Dict, optional
    :return: An instance of the specified algorithm.
    :rtype: RankAggAlgorithm
    :raises TypeError: If alg is not an instance of Algorithm, or if parameters is not a dict.
    """
    if not isinstance(alg, Algorithm):
        raise TypeError("alg must be an instance of Algorithm")
    if parameters is not None and not isinstance(parameters, Dict):
        raise TypeError("parameters must be a dict or None")

    if parameters is None:
        parameters = {}
    res: RankAggAlgorithm = (AlgorithmEnumeration.median_ranking_algorithms[alg.value])(**parameters)
    return res
