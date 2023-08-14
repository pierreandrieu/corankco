"""
Module for Copeland algorithm. More details in CopelandMethod docstring class.
"""

from typing import List, Dict, Tuple
from collections import defaultdict
from numpy import ndarray
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm
from corankco.algorithms.pairwisebasedalgorithm import PairwiseBasedAlgorithm
from corankco.dataset import Dataset
from corankco.ranking import Ranking
from corankco.consensus import Consensus
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import ConsensusFeature
from corankco.element import Element


class CopelandMethod(RankAggAlgorithm, PairwiseBasedAlgorithm):
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

        # associates for each element its generalized Copeland score within the Kemeny prism
        mapping_elem_score: Dict[int, float] = {}

        # associates for each element its number of victories - equality - defeat against other elements
        mapping_elem_victories: Dict[int, List[int]] = {}

        # iterates on elements to initialize the two dicts
        for element in range(dataset.nb_elements):
            # initially, elements have a score of 0.
            mapping_elem_score[element] = 0.
            # and no victories, equalities, defeats
            mapping_elem_victories[element] = [0, 0, 0]

        # now, update the two dicts: computes for each element the number of victories, equalities, defeats
        # for each pair of elements
        CopelandMethod._pairwise_cost_matrix_generic(
            dataset.get_positions(),
            scoring_scheme,
            CopelandMethod._fill_dicts_copeland,
            (mapping_elem_score, mapping_elem_victories)
        )

        # construction of Copeland ranking, sorting the elements by decreasing score
        dict_to_sort: defaultdict = defaultdict(set)
        mapping_id_elem: Dict[int, Element] = dataset.mapping_id_elem
        for key, value in mapping_elem_score.items():
            dict_to_sort[value].add(mapping_id_elem[key])

        # sort by values and convert values in sets
        copeland_ranking = [value for key, value in sorted(dict_to_sort.items(), reverse=True)]
        return Consensus([Ranking(copeland_ranking)],
                                      dataset=dataset,
                                      scoring_scheme=scoring_scheme,
                                      att={
                                          ConsensusFeature.ASSOCIATED_ALGORITHM: self.get_full_name(),
                                          ConsensusFeature.COPELAND_SCORES: {
                                              mapping_id_elem[id_elem]: elem
                                              for id_elem, elem in mapping_elem_score.items()
                                          },
                                          ConsensusFeature.COPELAND_VICTORIES: {
                                              mapping_id_elem[id_elem]: elem
                                              for id_elem, elem in mapping_elem_victories.items()
                                          }
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

    @staticmethod
    def _fill_dicts_copeland(cost_positions: ndarray, el1: int, el2: int,
                             structure: Tuple[Dict[int, float], Dict[int, List[int]]]):
        mapping_elem_score = structure[0]
        mapping_elem_victories = structure[1]

        put_before: float = cost_positions[0]
        put_after: float = cost_positions[1]
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
