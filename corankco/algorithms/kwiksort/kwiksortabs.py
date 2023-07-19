"""
Module for KwikSortAbs. This module contains an abstract class about KwikSort algorithm for rank aggregation. This
algorithm is based on QuickSort: a pivot is chosen, and the elements that should be placed before (resp. tied with,
resp. after) the pivot are placed before (resp. tied with, resp. after) the pivot, and this process is done recursively.
Complexity (mean): m * n * log(n) with n = nb of elements, m = nb of rankings.
A class that implements the abstract class must implement the choice of the pivot.
"""

from typing import List, Dict
from numpy import ndarray, asarray
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.element import Element
from corankco.ranking import Ranking


class KwikSortAbs(RankAggAlgorithm):
    """
    Interface for KwikSort algorithms. KwikSort is a heuristics designed for Kemeny-Young method.
    QuickSort based algorithm: pick a pivot, find the set of elements shat should be ranked after pivot,
    then before pivot, then tied with pivot, and recursively go on with the before and after sets
    complexity: mean: O(nb_rankings * nb_elements * log2(nb_elements)) if choice of pivot is O(1)
    complexity: worst: 0(nb_ranking * nb_elements²) if pivot divides elements in groups of size 1 and n-1
    """

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking: bool = True,
            bench_mode: bool = False
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
        :raise ScoringSchemeNotHandledException: When the algorithm cannot compute the consensus because the
        implementation does not support the given scoring scheme.
        """

        scoring_scheme_numpy: ndarray = asarray(scoring_scheme.penalty_vectors)

        consensus_list: List[List[Element]] = []
        mapping_elements_id: Dict[Element, int] = dataset.mapping_elem_id
        positions = dataset.get_positions()

        self._kwik_sort(consensus_list, list(dataset.universe), mapping_elements_id, positions, scoring_scheme_numpy)
        return Consensus(
            consensus_rankings=[Ranking([set(bucket) for bucket in consensus_list])], dataset=dataset,
            scoring_scheme=scoring_scheme, att={ConsensusFeature.ASSOCIATED_ALGORITHM: self.get_full_name()})

    def _get_pivot(self, mapping_elements_id: Dict[Element, int], elements: List[Element], positions: ndarray,
                   scoring_scheme: ndarray) -> Element:
        """
        Private function, returns the pivot. The choice of the pivot is set by the programmer in daughter classes
        :param mapping_elements_id: the dictionary whose keys are the elements and the values their unique int ID
        :param elements: the list of remaining elements to put in the consensus
        :param positions: ndarray where positions[i][j] is the position of element i in ranking j. Missing: element: -1
        :param scoring_scheme: the scoring scheme that may be used (or not) to choose a pivot
        :return: an Element as pivot
        """
        raise NotImplementedError("The method not implemented")

    # public abstract V getPivot(List < V > elements, U var);

    def _where_should_it_be(self, pos_pivot_rankings: ndarray, pos_other_element_rankings: ndarray,
                            scoring_scheme_numpy: ndarray) -> int:
        """
        Private method. Given the pivot defined by its ranks in the input rankings as a ndarray and another element
        defined by the same way, returns -1, 1, 0 if the element should be respectively before, after or tied with
        the pivot in the consensus
        :param pos_pivot_rankings: the nb_rankings positions of the pivot in a ndarray
        :param pos_other_element_rankings: the nb_rankings positions of the target element in a ndarray
        :param scoring_scheme_numpy: the ScoringScheme
        :return: returns -1, 1, 0 if the element should be respectively before, after or tied with the pivot
        in the consensus
        """
        raise NotImplementedError("The method not implemented")

    def _kwik_sort(self, consensus: List[List[Element]], remaining_elements: List[Element],
                   mapping_element_id: Dict[Element, int], positions: ndarray, scoring_scheme: ndarray):
        after: List[Element] = []
        before: List[Element] = []
        pivot: Element = Element(-1)
        if len(mapping_element_id) > 0:
            pivot = self._get_pivot(mapping_element_id, remaining_elements, positions, scoring_scheme)
        same: List[Element] = [pivot]
        positions_pivot = positions[mapping_element_id.get(pivot)]

        # compare pivot with all remaining elements to separate between "left", "center", "right"
        for element in remaining_elements:
            if element != pivot:
                positions_element = positions[mapping_element_id.get(element)]
                pos = self._where_should_it_be(positions_pivot, positions_element, scoring_scheme)
                if pos < 0:
                    before.append(element)
                elif pos > 0:
                    after.append(element)
                else:
                    same.append(element)

        if len(before) == 1:
            consensus.append(before)
        elif len(before) > 0:
            self._kwik_sort(consensus, before, mapping_element_id, positions, scoring_scheme)
        if len(same) > 0:
            consensus.append(same)
        if len(after) == 1:
            consensus.append(after)
        elif len(after) > 0:
            self._kwik_sort(consensus, after, mapping_element_id, positions, scoring_scheme)

    def get_full_name(self) -> str:
        """
        Return the full name of the algorithm.

        :return: name of the algorithm, must be defined in daughter classes.
        :rtype: str
        """
        raise NotImplementedError("The method not implemented")

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ndarray) -> bool:
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True as KwikSort can handle any ScoringScheme
        :rtype: bool
        """
        raise NotImplementedError("The method not implemented")
