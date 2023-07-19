"""
Module for KwikSortRandom. This module contains a class that implements the KwikSortAbs interface. The pivot is chosen
randomly.
"""

from typing import List, Dict
from random import choice
from numpy import count_nonzero, vdot, ndarray
from corankco.algorithms.kwiksort.kwiksortabs import KwikSortAbs
from corankco.element import Element
from corankco.scoringscheme import ScoringScheme


class KwikSortRandom(KwikSortAbs):
    """
    Implementation of KwikSort algorithm (see KwikSortAbs abstract class) with choice of pivot is random, uniform
    """

    def _get_pivot(self, mapping_elements_id: Dict[Element, int], elements: List[Element], positions: ndarray,
                   scoring_scheme: ndarray) -> Element:
        """
        Private function, returns the pivot. The pivot is chosen randomly in the elements List

        :param mapping_elements_id: The dictionary whose keys are the elements and the values their unique int ID
        :param elements: The list of remaining elements to put in the consensus
        :param positions: ndarray where positions[i][j] is the position of element i in ranking j. Missing: element: -1
        :param scoring_scheme: The scoring scheme  as ndarray that may be used (or not) to choose a pivot
        :return: An Element as pivot, randomly
        """
        return choice(elements)

    def _where_should_it_be(self, pos_pivot_rankings: ndarray, pos_other_element_rankings: ndarray,
                            scoring_scheme_numpy: ndarray) -> int:
        """
        Given the pivot defined by its ranks in the input rankings as a ndarray and another element
        defined by the same way, returns -1, 1, 0 if the element should be respectively before, after or tied with
        the pivot in the consensus.

        :param pos_pivot_rankings: the nb_rankings positions of the pivot in a ndarray
        :param pos_other_element_rankings: the nb_rankings positions of the target element in a ndarray
        :param scoring_scheme_numpy: the ScoringScheme as a numpy ndarray
        :return: returns 0 if the cost of tying the pivot and the element is minimal (not necessarily the unique minimal
        cost), -1 if the cost of having the element before the pivot in the consensus is minimal and the cost of tying
        them is not, 1 otherwise
        """
        # nb of rankings such that both pivot and other non-ranked
        both_non_ranked: int = count_nonzero(pos_pivot_rankings + pos_other_element_rankings == -2)
        # nb of rankings such that both pivot and other have same position or both non-ranked
        same_position: int = count_nonzero(pos_pivot_rankings == pos_other_element_rankings)
        # nb of rankings such that pivot is non-ranked
        pivot_missing: int = count_nonzero(pos_pivot_rankings == -1)
        # nb of rankings such that other is non-ranked
        other_missing: int = count_nonzero(pos_other_element_rankings == -1)
        # nb of rankings such that other is before pivot or other is non-ranked whereas pivot is ranked
        other_bef_pivot_or_missing: int = count_nonzero(pos_other_element_rankings < pos_pivot_rankings)

        # vector of all situations
        comp: List[int] = [other_bef_pivot_or_missing - other_missing + both_non_ranked,
                           len(pos_pivot_rankings) - other_bef_pivot_or_missing - same_position - pivot_missing
                           + both_non_ranked,
                           same_position - both_non_ranked,
                           pivot_missing - both_non_ranked,
                           other_missing - both_non_ranked,
                           both_non_ranked]
        # cost to place other before pivot
        cost_before = vdot(scoring_scheme_numpy[0], comp)
        # cost to tie other and pivot
        cost_same = vdot(scoring_scheme_numpy[1], comp)
        # cost to place other after pivot
        cost_after = vdot(scoring_scheme_numpy[0],
                          [len(pos_pivot_rankings) - other_bef_pivot_or_missing - same_position - pivot_missing
                           + both_non_ranked,
                           other_bef_pivot_or_missing - other_missing + both_non_ranked,
                           same_position - both_non_ranked,
                           other_missing - both_non_ranked,
                           pivot_missing - both_non_ranked,
                           both_non_ranked])

        # defining the group of the other element
        if cost_same <= cost_before:
            if cost_same <= cost_after:
                return 0
            return 1
        if cost_before <= cost_after:
            return -1
        return 1

    def get_full_name(self) -> str:
        """
        Return the full name of the algorithm.

        :return: The string 'KwikSortRandom'.
        :rtype: str
        """
        return "KwikSortRandom"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True as KwikSort can handle any ScoringScheme
        :rtype: bool
        """
        return True
