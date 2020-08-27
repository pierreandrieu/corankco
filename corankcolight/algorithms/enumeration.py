from enum import Enum, unique
from corankcolight.algorithms.allTied.alltied import AllTied
from corankcolight.algorithms.bioconsert.bioconsert import BioConsert
from corankcolight.algorithms.bioconsert.bioconsertc import BioConsertC


class AlgorithmEnumeration:
    median_ranking_algorithms = [
        AllTied,
        BioConsert,
        BioConsertC,
    ]


@unique
class Algorithm(Enum):
    AllTied = 0
    BioConsert = 1
    BioConsertC = 2
