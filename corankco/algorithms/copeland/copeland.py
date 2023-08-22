"""
Module for Copeland algorithm. More details in CopelandMethod docstring class.
"""

from typing import List, Dict, Set
from numpy import ndarray, zeros, argsort
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
        mapping_elem_score: ndarray

        # associates for each element its number of victories - equality - defeat against other elements
        mapping_elem_victories: ndarray

        mapping_id_elem: Dict[int, Element] = dataset.mapping_id_elem

        pairwise_cost_matrix: ndarray = CopelandMethod.pairwise_cost_matrix(
            dataset.get_positions(),
            scoring_scheme
        )

        # scores: nb_elements 1D ndarray, scores[i] = Copeland score of element with ID = i
        # results: (nb_elements, 3) 2D ndarray, scores[i] = number of victories, equalities, defeats of element
        # with ID = i
        scores_np, results_np = CopelandMethod._fill_dicts_copeland(pairwise_cost_matrix)

        sorted_indices = argsort(scores_np)[::-1]  # Trie les indices en ordre décroissant de scores.
        current_score = scores_np[sorted_indices[0]]
        current_set: Set[Element] = {mapping_id_elem[sorted_indices[0]]}

        # construction of Copeland ranking, sorting the elements by decreasing score
        copeland_ranking: List[Set[Element]] = []

        for idx in sorted_indices[1:]:
            if scores_np[idx] == current_score:
                current_set.add(mapping_id_elem[idx])
            else:
                copeland_ranking.append(current_set)
                current_set = {mapping_id_elem[idx]}
                current_score = scores_np[idx]

        copeland_ranking.append(current_set)
        return Consensus([Ranking(copeland_ranking)],
                                      dataset=dataset,
                                      scoring_scheme=scoring_scheme,
                                      att={
                                          ConsensusFeature.ASSOCIATED_ALGORITHM: self.get_full_name(),
                                          ConsensusFeature.COPELAND_SCORES: {mapping_id_elem[i]: scores_np[i] for i
                                                                             in range(len(scores_np))},
                                          ConsensusFeature.COPELAND_VICTORIES: {mapping_id_elem[i]: list(results_np[i])
                                                                                for i in range(len(results_np))}
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
    def _fill_dicts_copeland(pairwise_cost_matrix: ndarray):
        nb_elements, _, _ = pairwise_cost_matrix.shape

        scores = zeros(nb_elements)
        results = zeros((nb_elements, 3))

        for el1 in range(nb_elements):
            for el2 in range(el1 + 1, nb_elements):
                put_before: float = pairwise_cost_matrix[el1][el2][0]
                put_after: float = pairwise_cost_matrix[el1][el2][1]
                if put_before < put_after:
                    scores[el1] += 1
                    results[el1, 0] += 1
                    results[el2, 2] += 1
                elif put_after < put_before:
                    scores[el2] += 1
                    results[el1, 2] += 1
                    results[el2, 0] += 1
                else:
                    scores[el1] += 0.5
                    scores[el2] += 0.5
                    results[el1, 1] += 1
                    results[el2, 1] += 1

        return scores, results
