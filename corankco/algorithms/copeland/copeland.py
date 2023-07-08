from collections import defaultdict
from typing import List, Dict
from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.ranking import Ranking
from corankco.consensus import Consensus
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import ConsensusSingleRanking, ConsensusFeature
from corankco.element import Element


class CopelandMethod(MedianRanking):
    """
    Copeland's method is one of the most famous electoral system published in :
    A. H. Copeland, A reasonable social welfare function, seminar on Applications of Mathematics to the social
    sciences, University of Michigan, 1951.
    Complexity: O(nb_elements² * nb_rankings)
    This method can be easily adapted to incomplete rankings with ties using the framework of Andrieu et al., 2023
    A victory for x against y becomes before(x,y) < before(y,x), score += 1 for x and += 0 for y
    An equality for x against y becomes before(x,y) = before(y,x), score += 0.5 for both x and y
    """
    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking=True,
            bench_mode=False
    ) -> ConsensusSingleRanking:
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

        # associates for each element its generalized Copeland score within the Kemeny prism
        mapping_elem_score: Dict[Element, float] = {}

        # associates for each element its number of victories - equality - defeat against other elements
        mapping_elem_victories: Dict[Element, List[int]] = {}

        # iterates on elements to initialize the two dicts
        for element in dataset.universe:
            # initially, elements have a score of 0.
            mapping_elem_score[element] = 0.
            # and no victories, equalities, defeats
            mapping_elem_victories[element] = [0, 0, 0]

        # now, update the two dicts: computes for each element the number of victories, equalities, defeats
        # for each pair of elements
        for pairwise_comparison in dataset.penalties_relative_positions(scoring_scheme):
            el1: Element = pairwise_comparison.x
            el2: Element = pairwise_comparison.y

            put_before: float = pairwise_comparison.x_before_y
            put_after: float = pairwise_comparison.x_after_y

            if put_before < put_after:
                mapping_elem_score[el1] += 1
                mapping_elem_victories[el1][0] += 1
                mapping_elem_victories[el2][2] += 1
            elif put_after < put_before:
                mapping_elem_score[el2] += 1
                mapping_elem_victories[el1][2] += 1
                mapping_elem_victories[el2][0] += 1
            else:
                mapping_elem_score[el1] += 0.5
                mapping_elem_score[el2] += 0.5
                mapping_elem_victories[el1][1] += 1
                mapping_elem_victories[el2][1] += 1

        # construction of Copeland ranking, sorting the elements by decreasing score
        d: defaultdict = defaultdict(set)
        for key, value in mapping_elem_score.items():
            d[value].add(key)

        # Trier par valeurs et convertir les valeurs en ensembles
        copeland_ranking = [value for key, value in sorted(d.items(), reverse=True)]
        return ConsensusSingleRanking(Ranking(copeland_ranking),
                                      dataset=dataset,
                                      scoring_scheme=scoring_scheme,
                                      att={
                              ConsensusFeature.AssociatedAlgorithm: self.get_full_name(),
                              ConsensusFeature.CopelandScores: mapping_elem_score,
                              ConsensusFeature.CopelandVictories: mapping_elem_victories
                              }
                         )

    def get_full_name(self) -> str:
        """
        Return the full name of the algorithm.

        :return: The string 'CopelandMethod'.
        :rtype: str
        """
        return "CopelandMethod"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True as CopelandMethod can handle any ScoringScheme
        :rtype: bool
        """
        return True
