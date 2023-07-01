from enum import Enum, unique
from typing import Dict, List
from corankco.algorithms.median_ranking import MedianRanking
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.parcons.parcons import ParCons
from corankco.algorithms.exact.exactalgorithm import ExactAlgorithm
from corankco.algorithms.kwiksort.kwiksortrandom import KwikSortRandom
from corankco.algorithms.repeatchoice.repeatchoice import RepeatChoice
from corankco.algorithms.pickaperm.pickaperm import PickAPerm
from corankco.algorithms.medrank.medrank import MedRank
from corankco.algorithms.borda.borda import BordaCount
from corankco.algorithms.bioconsert.bioco import BioCo
from corankco.algorithms.copeland.copeland import CopelandMethod


class AlgorithmEnumeration:
    """Contains a list of classes for all available ranking algorithms."""
    median_ranking_algorithms = [
        BioConsert,
        ParCons,
        ExactAlgorithm,
        KwikSortRandom,
        RepeatChoice,
        PickAPerm,
        MedRank,
        BordaCount,
        BioCo,
        CopelandMethod,
    ]


@unique
class Algorithm(Enum):
    """Enum representing the available ranking algorithms."""
    BioConsert = 0
    ParCons = 1
    Exact = 2
    KwikSortRandom = 3
    RepeatChoice = 4
    PickAPerm = 5
    MedRank = 6
    BordaCount = 7
    BioCo = 8
    CopelandMethod = 9
    AllTied = 10

    @staticmethod
    def get_all() -> List['Algorithm']:
        """
        Returns a list of all available algorithms.

        :return: A List of all the available algorithms.
        :rtype: List[Algorithm]
        """
        return [Algorithm.AllTied, Algorithm.BioConsert, Algorithm.ParCons,
                Algorithm.Exact, Algorithm.KwikSortRandom, Algorithm.RepeatChoice, Algorithm.PickAPerm,
                Algorithm.MedRank, Algorithm.BordaCount, Algorithm.BioCo, Algorithm.CopelandMethod]

    @staticmethod
    def get_all_compatible_with_any_scoring_scheme() -> List['Algorithm']:
        """
        Returns a list of algorithms that are compatible with any scoring scheme.

        The returned algorithms have implementations that can handle any scoring scheme.

        :return: A List of all the algorithms compatible with any scoring scheme.
        :rtype: List[Algorithm]
        """
        return [Algorithm.BioConsert, Algorithm.ParCons, Algorithm.Exact,
                Algorithm.KwikSortRandom, Algorithm.CopelandMethod]


def get_algorithm(alg: Algorithm, parameters: Dict = None) -> MedianRanking:
    """
    Returns an instance of the specified algorithm.

    :param alg: The algorithm to instantiate. Must be an instance of the Algorithm enum.
    :type alg: Algorithm
    :param parameters: The parameters to pass to the algorithm's constructor. If None, an empty dict will be used.
    :type parameters: Dict, optional
    :return: An instance of the specified algorithm.
    :rtype: MedianRanking
    :raises TypeError: If alg is not an instance of Algorithm, or if parameters is not a dict.
    """
    if not isinstance(alg, Algorithm):
        raise TypeError("alg must be an instance of Algorithm")
    if parameters is not None and not isinstance(parameters, Dict):
        raise TypeError("parameters must be a dict or None")

    if parameters is None:
        parameters = {}
    res = (AlgorithmEnumeration.median_ranking_algorithms[alg.value])(**parameters)
    return res
