from enum import Enum, unique
from corankcolight.algorithms.allTied.alltied import AllTied
from corankcolight.algorithms.bioconsert.bioconsert import BioConsert
from corankcolight.algorithms.parcons.parcons import ParCons


class AlgorithmEnumeration:
    median_ranking_algorithms = [
        AllTied,
        BioConsert,
        ParCons
    ]


@unique
class Algorithm(Enum):
    AllTied = 0
    BioConsert = 1
    ParCons = 2
