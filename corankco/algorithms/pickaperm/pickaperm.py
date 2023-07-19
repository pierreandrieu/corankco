"""
Module for PickAPerm algorithm. More details in PickAPerm docstring class.
"""

from typing import List, Dict
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.kemeny_score_computation import KemenyComputingFactory
from corankco.ranking import Ranking


class InompleteRankingsIncompatibleWithScoringSchemeException(Exception):
    """
    Exception if the input rankings are incomplete, and the chosen scoring scheme does not make understand that the
    rankings can be unified.
    """


class PickAPerm(RankAggAlgorithm):
    """
    Algorithm for rank aggregation initially defined in N.Ailon, M.Charikar, A.Newman. Aggregating inconsistent
    information : ranking and clustering. Journal of the ACM (JACM) 55.5 (2008), p. 23.
    This algorithm has been designed as a 2-approximation algorithm of the Kemeny-Young method when rankings are
    complete and without ties. It selects the input ranking which minimizes the Kemeny score with the input rankings.

    Generalization to incomplete rankings (with ties): Within the framework designed by P.Andrieu, S.Cohen-Boulakia,
    M.Couceiro, A.Denise, A.Pierrot. A Unifying Rank Aggregation Model to Suitably and Efficiently Aggregate Any Kind of
    Rankings. https://dx.doi.org/10.2139/ssrn.4353494, this algorithm can only be used with one ScoringScheme
    (see is_scoring_scheme_relevant_when_incomplete_rankings docstring, and ScoringScheme class)
    """

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking: bool = True,
            bench_mode: bool = False
    ) -> Consensus:
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The penalty vectors to consider
        :type scoring_scheme: ScoringScheme (class ScoringScheme in package 'distances')
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :param bench_mode: is bench mode activated. If False, the algorithm may return more information
        :type bench_mode: bool
        :return one or more rankings if the underlying algorithm can find several equivalent consensus rankings
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found.
        In all scenario, the algorithm returns a list of consensus rankings
        :raise ScoringSchemeNotHandledException when the algorithm cannot compute the consensus because the
        implementation of the algorithm does not fit with the scoring scheme
        """
        if not dataset.is_complete:
            if not scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme()):
                raise InompleteRankingsIncompatibleWithScoringSchemeException
            rankings_to_use = dataset.unified_rankings()
        else:
            rankings_to_use = dataset.rankings

        mapping_ranking_score: Dict[str, float] = {}
        kemeny_computation: KemenyComputingFactory = KemenyComputingFactory(scoring_scheme)

        dst_min = float('inf')
        consensus: List[Ranking] = []
        for ranking in rankings_to_use:
            ranking_str: str = str(ranking)
            if ranking_str not in mapping_ranking_score:
                dist: float = kemeny_computation.get_kemeny_score(ranking, dataset)
            else:
                dist: float = mapping_ranking_score[ranking_str]
            if dist < dst_min:
                dst_min = dist
                consensus.clear()
                consensus.append(ranking)
            elif dist == dst_min and not return_at_most_one_ranking:
                consensus.append(ranking)

        return Consensus(consensus_rankings=consensus,
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={ConsensusFeature.KEMENY_SCORE: dst_min,
                              ConsensusFeature.ASSOCIATED_ALGORITHM: self.get_full_name()
                              }
                         )

    def get_full_name(self) -> str:
        """
        Return the full name of the algorithm.

        :return: The string 'Pick a Perm'.
        :rtype: str
        """
        return "Pick a Perm"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True if the scoring scheme is equivalent to unifying scoring scheme
        Otherwise, False. Indeed, the consensus ranking need to be complete in this framework. Selecting this
        ScoringScheme mean that the user agrees with considering all the missing elements of an input ranking r can be
        considered as tied in a unifying bucket at the end of r, which makes the input rankings "virtually complete".
        """
        return scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme())
