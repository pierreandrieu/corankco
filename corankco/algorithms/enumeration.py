from enum import Enum, unique
from corankco.algorithms.allTied.alltied import AllTied
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
    median_ranking_algorithms = [
        AllTied,
        BioConsert,
        ParCons,
        ExactAlgorithm,
        KwikSortRandom,
        RepeatChoice,
        PickAPerm,
        MedRank,
        BordaCount,
        BioCo,
        CopelandMethod
    ]


@unique
class Algorithm(Enum):
    AllTied = 0
    BioConsert = 1
    ParCons = 2
    Exact = 3
    KwikSortRandom = 4
    RepeatChoice = 5
    PickAPerm = 6
    MedRank = 7
    BordaCount = 8
    BioCo = 9
    CopelandMethod = 10

    @staticmethod
    def get_all():
        return [Algorithm.AllTied, Algorithm.BioConsert, Algorithm.ParCons,
                Algorithm.Exact, Algorithm.KwikSortRandom, Algorithm.RepeatChoice, Algorithm.PickAPerm,
                Algorithm.MedRank, Algorithm.BordaCount, Algorithm.BioCo, Algorithm.CopelandMethod]
    @staticmethod
    def get_all_compatible_with_any_scoring_scheme():
        return [Algorithm.BioConsert, Algorithm.ParCons, Algorithm.Exact,
                Algorithm.KwikSortRandom, Algorithm.CopelandMethod]


