from corankcolight.consensus import Consensus
from corankcolight.dataset import Dataset
from corankcolight.scoringscheme import ScoringScheme
from corankcolight.algorithms.enumeration import AlgorithmEnumeration, Algorithm


class KemRankAgg:
    def __init__(self):
        pass

    @staticmethod
    def compute_consensus(dataset: Dataset, scoring_scheme: ScoringScheme, algorithm: Algorithm) -> Consensus:
        alg = AlgorithmEnumeration.median_ranking_algorithms[algorithm.value]
        return alg().compute_consensus_rankings(dataset, scoring_scheme, False)
