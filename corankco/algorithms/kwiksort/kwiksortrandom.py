from typing import List, Dict
from numpy import count_nonzero, vdot, ndarray
from random import choice
from corankco.algorithms.kwiksort.kwiksortabs import KwikSortAbs
from corankco.element import Element
from corankco.scoringscheme import ScoringScheme


class KwikSortRandom(KwikSortAbs):
    """
    Implementation of KwikSort algorithm (see KwikSortAbs abstract class) with choice of pivot is random, uniform
    """

    def _get_pivot(self, mapping_elements_id: Dict[Element, int], elements: List[Element], positions: ndarray,
                   scoring_scheme: ScoringScheme) -> Element:
        """
        Private function, returns the pivot. The pivot is chosen randomly in the elements List
        :param mapping_elements_id: the dictionary whose keys are the elements and the values their unique int ID
        :param elements: the list of remaining elements to put in the consensus
        :param positions: ndarray where positions[i][j] is the position of element i in ranking j. Missing: element: -1
        :param scoring_scheme: the scoring scheme that may be used (or not) to choose a pivot
        :return: an Element as pivot, randomly
        """
        return choice(elements)

    def _where_should_it_be(self, pos_pivot: ndarray, pos_other_element: ndarray, scoring_scheme_numpy: ndarray) -> int:
        """
        Given the pivot defined by its ranks in the input rankings as a ndarray and another element
        defined by the same way, returns -1, 1, 0 if the element should be respectively before, after or tied with
        the pivot in the consensus.

        :param pos_pivot: the nb_rankings positions of the pivot in a ndarray
        :param pos_other_element: the nb_rankings positions of the target element in a ndarray
        :param scoring_scheme_numpy: the ScoringScheme as a numpy ndarray
        :return: returns 0 if the cost of tying the pivot and the element is minimal (not necessarily the unique minimal
        cost), -1 if the cost of having the element before the pivot in the consensus is minimal and the cost of tying
        them is not, 1 otherwise
        """
        a: int = count_nonzero(pos_pivot + pos_other_element == -2)
        b: int = count_nonzero(pos_pivot == pos_other_element)
        c: int = count_nonzero(pos_pivot == -1)
        d: int = count_nonzero(pos_other_element == -1)
        e: int = count_nonzero(pos_other_element < pos_pivot)

        comp: List[int] = [e-d+a, len(pos_pivot)-e-b-c+a, b-a, c-a, d-a, a]
        cost_before = vdot(scoring_scheme_numpy[0], comp)
        cost_same = vdot(scoring_scheme_numpy[1], comp)
        cost_after = vdot(scoring_scheme_numpy[0], [len(pos_pivot)-e-b-c+a,  e-d+a, b-a, d-a, c-a, a])

        if cost_same <= cost_before:
            if cost_same <= cost_after:
                return 0
            return 1
        else:
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
