from enum import Enum, unique
from typing import Dict
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
from corankco.algorithms.alltied.all_tied import AllTied


class AlgorithmEnumeration:
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
        AllTied
    ]


@unique
class Algorithm(Enum):
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
    def get_all():
        return [Algorithm.AllTied, Algorithm.BioConsert, Algorithm.ParCons,
                Algorithm.Exact, Algorithm.KwikSortRandom, Algorithm.RepeatChoice, Algorithm.PickAPerm,
                Algorithm.MedRank, Algorithm.BordaCount, Algorithm.BioCo, Algorithm.CopelandMethod]

    @staticmethod
    def get_all_compatible_with_any_scoring_scheme():
        return [Algorithm.BioConsert, Algorithm.ParCons, Algorithm.Exact,
                Algorithm.KwikSortRandom, Algorithm.CopelandMethod]


def get_algorithm(alg: Algorithm, parameters: Dict = None) -> MedianRanking:
    if parameters is None:
        parameters = {}
    res = (AlgorithmEnumeration.median_ranking_algorithms[alg.value])(**parameters)
    return res
