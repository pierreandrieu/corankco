from corankco.consensus import Consensus
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.enumeration import AlgorithmEnumeration, Algorithm


class KemRankAgg:
    def __init__(self):
        pass

    @staticmethod
    def compute_consensus(dataset: Dataset,
                          scoring_scheme: ScoringScheme,
                          algorithm: Algorithm,
                          single_consensus=False) -> Consensus:
        alg = AlgorithmEnumeration.median_ranking_algorithms[algorithm.value]
        return alg().compute_consensus_rankings(dataset, scoring_scheme, single_consensus)
