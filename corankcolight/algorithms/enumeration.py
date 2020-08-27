from enum import Enum, unique
from corankcolight.algorithms.allTied.alltied import AllTied
from corankcolight.algorithms.bioconsert.bioconsert import BioConsert


class AlgorithmEnumeration:
    median_ranking_algorithms = [
        AllTied,
        BioConsert,
    ]


@unique
class Algorithm(Enum):
    AllTied = 0
    BioConsert = 1
