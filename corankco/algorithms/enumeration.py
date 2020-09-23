from enum import Enum, unique
from corankco.algorithms.allTied.alltied import AllTied
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.algorithms.parcons.parcons import ParCons
from corankco.algorithms.exact.exactalgorithm import ExactAlgorithm


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
