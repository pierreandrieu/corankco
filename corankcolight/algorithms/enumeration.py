from enum import Enum, unique
from corankcolight.algorithms.allTied.alltied import AllTied
from corankcolight.algorithms.bioconsert.bioconsert import BioConsert
from corankcolight.algorithms.parcons.parcons import ParCons
from corankcolight.algorithms.exact.exactalgorithm import ExactAlgorithm


class AlgorithmEnumeration:
    median_ranking_algorithms = [
        AllTied,
        BioConsert,
        ParCons,
        ExactAlgorithm,
    ]


@unique
class Algorithm(Enum):
    AllTied = 0
    BioConsert = 1
    ParCons = 2
    Exact = 3
