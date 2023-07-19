"""
Module that allows to choose a rank aggregation algorithm from an enumeration.
"""

from .algorithm_choice import get_algorithm, Algorithm, AlgorithmEnumeration
from .pairwisebasedalgorithm import PairwiseBasedAlgorithm
from .rank_aggregation_algorithm import RankAggAlgorithm
from .exact import ExactAlgorithm
from .borda import BordaCount
from .copeland import CopelandMethod
from .pickaperm import PickAPerm
from .parcons import ParCons
from .bioconsert import BioConsert, BioCo
from .kwiksort import KwikSortRandom
