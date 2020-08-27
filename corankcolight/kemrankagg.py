from corankcolight.consensus import Consensus
from corankcolight.dataset import Dataset
from corankcolight.scoringscheme import ScoringScheme
from corankcolight.algorithms.enumeration import AlgorithmEnumeration, Algorithm


class KemRankAgg:
    def __init__(self):
        pass

    # def compute_exact_solutions(self, dataset: Dataset, scoring_scheme: ScoringScheme, exhaustive: bool) -> Consensus:
    #

    @staticmethod
    def compute_with_heuristic(dataset: Dataset, scoring_scheme: ScoringScheme, algorithm: Algorithm) -> Consensus:
        alg = AlgorithmEnumeration.median_ranking_algorithms[algorithm.value]
        return alg().compute_consensus_rankings(dataset=dataset,
                                                scoring_scheme=scoring_scheme,
                                                return_at_most_one_ranking=False)
