"""
Module for Borda algorithm. More details in Borda docstring class.
"""

from typing import Dict, List, Tuple, Set
from itertools import groupby
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm, ScoringSchemeNotHandledException
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.element import Element
from corankco.ranking import Ranking


class BordaCount(RankAggAlgorithm):
    """
    Borda is a rank aggregation method defined by Borda in J. C. de Borda, Mémoire sur les élections au scrutin,
    Histoire de l’académie royale des sciences, Paris, France, 1781, Ch. 1, pp. 657–664.
    It is one of the most famous voting system, used for example to elect the "Ballon d'or"
    This rank aggregation method has been slightly adapted to incomplete rankings with ties.
    Handling ties: score of an element in a ranking can be the rank of the element - 1, or the id bucket. The user can
    select its preference with the parameter use_bucket_id, boolean, False by default
    For instance, if ranking = [ {3, 5, 4}, {1, 2} ], if use_bucket_id = False, score(1) = score(2) = 3 whereas if
    use_bucket_id =  True, score(1) = score(2) = 1
    Handling non-ranked elements: depend on the Scoring Scheme used (see ScoringScheme class). Two of them are allowed
    (see method is_scoring_scheme_relevant_when_incomplete_rankings).
    According to the scoring scheme, elements will be ranked by score considering non-ranked elements as in a last
    bucket, or elements will be ranked according to their mean score when they are ranked.
    """
    def __init__(self,  use_bucket_id=False):
        """
        Initialize the BordaCount object.

        :param use_bucket_id: If True, an element e gets a score based on its bucket_id in each input ranking,
                              otherwise it gets a score based on the number of elements ranked strictly before e.
        :type use_bucket_id: bool
        """
        self._use_bucket_id_not_bucket_size = use_bucket_id

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking=False,
            bench_mode=False
    ) -> Consensus:
        """
        Calculate and return the consensus rankings based on the given dataset and scoring scheme.

        :param dataset: The dataset of rankings to be aggregated.
        :type dataset: Dataset
        :param scoring_scheme: The scoring scheme to be used for calculating consensus.
        :type scoring_scheme: ScoringScheme
        :param return_at_most_one_ranking: If True, the algorithm should return at most one ranking.
        :type return_at_most_one_ranking: bool
        :param bench_mode: If True, the algorithm may return additional information for benchmarking purposes.
        :type bench_mode: bool
        :return: Consensus rankings. If the algorithm is unable to provide multiple consensuses or
                 return_at_most_one_ranking is True, a single consensus ranking is returned.
        :rtype: Consensus
        :raise ScoringSchemeNotHandledException: When the algorithm cannot compute the consensus because the
                                                 implementation does not support the given scoring scheme.
        """

        if not dataset.is_complete and not self.is_scoring_scheme_relevant_when_incomplete_rankings(scoring_scheme):
            raise ScoringSchemeNotHandledException

        if scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme()) or \
                scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme_p(0.5)):
            rankings_to_use = dataset.unified_rankings()
        else:
            rankings_to_use = dataset.rankings

        # for a given element e, points[e][0] = number of points of e with borda count and points[e][1] =
        # number of rankings such that e is ranked

        # computing scores for each element in a Dict
        points: Dict[Element, List[int]] = {}
        for ranking in rankings_to_use:
            id_bucket: int = 0
            for bucket in ranking:
                for elem in bucket:
                    if elem not in points:
                        points[elem]: List[int] = [0, 0]
                    points[elem][0] += id_bucket
                    points[elem][1] += 1
                if self._use_bucket_id_not_bucket_size:
                    id_bucket += 1
                else:
                    id_bucket += len(bucket)

        elements_scores: List[Tuple[Element, float]] = \
            [(elem, scores[0] * 1.0 / scores[1]) for elem, scores in points.items()]
        # now, sort the elements by increasing order of score
        sorted_elements_scores_by_score = sorted(elements_scores, key=lambda col: col[1])

        # construct the consensus bucket by bucket
        consensus_list: List[Set[Element]] = []
        for _, group in groupby(sorted_elements_scores_by_score, lambda x: x[1]):
            consensus_list.append({elem for elem, _ in group})

        return Consensus(consensus_rankings=[Ranking(consensus_list)],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={
                              ConsensusFeature.ASSOCIATED_ALGORITHM: self.get_full_name()
                              }
                         )

    def get_full_name(self) -> str:
        """
        Return the full name of the algorithm.

        :return: The string 'BordaCount'.
        :rtype: str
        """
        return "BordaCount"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True if the scoring scheme is equivalent to one of the following:
                 - induced measure scoring scheme
                 - unifying scoring scheme
                 - induced measure scoring scheme with p=0.5
                 - unifying scoring scheme with p=0.5
                 Otherwise, False.
        :rtype: bool
        """
        return scoring_scheme.is_equivalent_to(ScoringScheme.get_induced_measure_scoring_scheme()) or \
               scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme()) or \
               scoring_scheme.is_equivalent_to(ScoringScheme.get_induced_measure_scoring_scheme_p(0.5))\
               or scoring_scheme.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme_p(0.5))
