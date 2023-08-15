"""
Module that implements generic functions about pairwise based rank aggregation algorithm. Module for code factorisation.
"""

from typing import Tuple, List, Callable, Any, Set
from itertools import combinations
from igraph import Graph
from numpy import ndarray, shape, zeros, newaxis, sum as np_sum
from corankco.scoringscheme import ScoringScheme


class PairwiseBasedAlgorithm:
    """

    Class to gather several useful methods for pairwise based algorithms. Class for code factorisation.
    """

    @staticmethod
    def _pairwise_cost_matrix_generic(
            positions: ndarray, scoring_scheme, callback: Callable[[ndarray, int, int, Any], Any], structure: Any) \
            -> ndarray:
        """
        Computes the pairwise cost matrix, and allows for calling a function for each pair of elements after computing
        the cost of the different relative positions. Useful for code factorisation.

        :param positions: The 2D ndarray matrix where positions[i][j] is the position of element int id i in ranking j
        :param scoring_scheme: The associated scoring scheme.
        :param callback: The function to call after computing before(x,y), before(y,x), tied(x,y)
        :param structure: A structure object, a parameter for the callback function.
        :return: The pairwise cost matrix as n * n * 3 ndarray, where n is the number of elements
        """

        nb_elem, nb_rankings = positions.shape

        # Create the matrix
        matrix = zeros((nb_elem, nb_elem, 3))

        # For each pair of elements el_1 and el_2
        el_1_positions = positions[:, newaxis, :]
        el_2_positions = positions[newaxis, :, :]

        # Calculate each condition for relative positions
        e1_before_e2 = np_sum((el_1_positions < el_2_positions) & (el_1_positions != -1) & (el_2_positions != -1),
                              axis=2)
        e2_before_e1 = np_sum((el_2_positions < el_1_positions) & (el_1_positions != -1) & (el_2_positions != -1),
                              axis=2)
        e1_e2_same_pos = np_sum((el_1_positions == el_2_positions) & (el_1_positions != -1), axis=2)
        e1_present_e2_absent = np_sum((el_1_positions != -1) & (el_2_positions == -1), axis=2)
        e2_present_e1_absent = np_sum((el_2_positions != -1) & (el_1_positions == -1), axis=2)
        e1_e2_both_absent = np_sum((el_1_positions == -1) & (el_2_positions == -1), axis=2)

        relative_positions = zeros((nb_elem, nb_elem, 6))
        relative_positions[:, :, 0] = e1_before_e2
        relative_positions[:, :, 1] = e2_before_e1
        relative_positions[:, :, 2] = e1_e2_same_pos
        relative_positions[:, :, 3] = e1_present_e2_absent
        relative_positions[:, :, 4] = e2_present_e1_absent
        relative_positions[:, :, 5] = e1_e2_both_absent

        # Compute costs
        cost_before = scoring_scheme.b_vector
        cost_after = [cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                      cost_before[5]]
        cost_tied = scoring_scheme.t_vector

        matrix[:, :, 0] = np_sum(relative_positions * cost_before, axis=2)
        matrix[:, :, 1] = np_sum(relative_positions * cost_after, axis=2)
        matrix[:, :, 2] = np_sum(relative_positions * cost_tied, axis=2)

        for el_1 in range(nb_elem):
            for el_2 in range(el_1 + 1, nb_elem):
                callback(matrix[el_1][el_2], el_1, el_2, structure)

        return matrix

    @staticmethod
    def graph_of_elements_with_robust_arcs(positions: ndarray, scoring_scheme: ScoringScheme) -> \
            Tuple[Graph, ndarray, Set[Tuple[int, int]]]:
        """
        Compute the graph of elements, the cost of pairwise relative positions and the set of robust arcs defined in the
        Future Generation Computer Systems article (as mentioned in the Class docstring)

        This function generates a graph of elements as defined in the Future Generation Computer Systems article
        (as mentioned in the Class docstring) and computes the cost of pairwise relative positions.
        The latter is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        i after j, i tied with j in the consensus according to the scoring scheme.

        :param positions: a matrix where pos[i][j] denotes the position of element i in ranking j (-1 if non-ranked)
        :param scoring_scheme: the scoring scheme to compute the cost matrix
        :return: A tuple containing the Graph of elements defined in the FGCS article, the 3D matrix of costs of
        pairwise relative positions, and the set of the robust arcs defined in the FGCS article
        """
        graph_of_elements: Graph = Graph(directed=True)
        arcs: List[Tuple[int, int]] = []
        robust_arcs: Set[Tuple[int, int]] = set()

        # add a vertex for each element
        for i in range(shape(positions)[0]):
            graph_of_elements.add_vertex(name=str(i))

        matrix: ndarray = PairwiseBasedAlgorithm._pairwise_cost_matrix_generic(
            positions, scoring_scheme, PairwiseBasedAlgorithm._fill_graph_and_robust_arcs, (arcs, robust_arcs)
        )

        # arcs should be added all at once, the impact on performances is clear
        graph_of_elements.add_edges(arcs)
        return graph_of_elements, matrix, robust_arcs

    @staticmethod
    def graph_of_elements(positions: ndarray, scoring_scheme: ScoringScheme) -> Tuple[Graph, ndarray]:
        """
        Compute the graph of elements, the cost of pairwise relative positions and the set of robust arcs defined in the
        Future Generation Computer Systems article (as mentioned in the Class docstring)

        This function generates a graph of elements as defined in the Future Generation Computer Systems article
        (as mentioned in the Class docstring) and computes the cost of pairwise relative positions.
        The latter is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        i after j, i tied with j in the consensus according to the scoring scheme.

        :param positions: a matrix where pos[i][j] denotes the position of element i in ranking j (-1 if non-ranked)
        :param scoring_scheme: the Scoring Scheme to compute the cost matrix
        :return: A tuple containing the Graph of elements defined in the FGCS article, the 3D matrix of costs of
        pairwise relative positions
        """
        graph_of_elements: Graph = Graph(directed=True)

        # add a vertex for each element
        for i in range(shape(positions)[0]):
            graph_of_elements.add_vertex(name=str(i))

        arcs: List[Tuple[int, int]] = []

        matrix: ndarray = PairwiseBasedAlgorithm._pairwise_cost_matrix_generic(
            positions, scoring_scheme, PairwiseBasedAlgorithm._fill_graph, arcs)

        # arcs should be added all at once, the impact on performances is clear
        graph_of_elements.add_edges(arcs)
        return graph_of_elements, matrix

    @staticmethod
    def pairwise_cost_matrix(positions: ndarray, scoring_scheme: ScoringScheme) -> ndarray:
        """
        Compute the cost of pairwise relative positions.

        This function computes the cost of pairwise relative positions.
        The latter is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        i after j, i tied with j in the consensus according to the scoring scheme.

        :param positions: a matrix where pos[i][j] denotes the position of element i in ranking j (-1 if non-ranked)
        :param scoring_scheme: the scoring scheme to compute the cost matrix
        :return: The 3D matrix of costs of pairwise relative positions.
        """
        return PairwiseBasedAlgorithm._pairwise_cost_matrix_generic(
            positions, scoring_scheme, PairwiseBasedAlgorithm._nothing_to_do, structure=None)

    @staticmethod
    def _nothing_to_do(cost_matrix: ndarray, el_1: int, el_2: int, structure: None) -> None:
        """
        Function to be called by a callback when nothing should be done
        :param cost_matrix: The 3D cost matrix
        :param el_1: The 1st element.
        :param el_2: The 2nd element.
        :param structure: object, type Any
        :return: None
        """

    @staticmethod
    def _fill_graph_and_robust_arcs(cost_matrix: ndarray, el_1: int, el_2: int,
                                    arcs_robust_arcs: Tuple[List[Tuple[int, int]], Set[Tuple[int, int]]]) -> None:
        """
        Function to be called by a callback when the graph of elements must be computed,
        with its set of robust arcs.

        :param cost_matrix: The 3D cost matrix.
        :param el_1: The 1st element.
        :param el_2: The 2nd element.
        :param arcs_robust_arcs: The list of arcs and the set of robust arcs to be modified when
               computing the cost matrix, as a Tuple.
        :return: None.
        """

        # if x should not be placed after y, then arc from x to y
        put_before: float = cost_matrix[0]
        put_after: float = cost_matrix[1]
        put_tied: float = cost_matrix[2]
        arcs: List[Tuple[int, int]] = arcs_robust_arcs[0]
        robust_arcs: Set[Tuple[int, int]] = arcs_robust_arcs[1]

        if put_before > put_after or put_before > put_tied:
            arcs.append((el_2, el_1))
        # if y should not be placed after x, then arc from y to x
        if put_after > put_before or put_after > put_tied:
            arcs.append((el_1, el_2))

        if put_before < put_after and put_before < put_tied:
            robust_arcs.add((el_1, el_2))
        if put_after < put_before and put_after < put_tied:
            robust_arcs.add((el_2, el_1))

    @staticmethod
    def _fill_graph(cost_matrix: ndarray, el_1: int, el_2: int, arcs: List[Tuple[int, int]]):
        """
        Function to be called by a callback when the graph of elements must be computed.

        :param cost_matrix: The 3D cost matrix.
        :param el_1: The 1st element.
        :param el_2: The 2nd element.
        :param arcs: The list of arcs to be modified as a List of Tuple of int, int.
        :return: None.
        """
        put_before: float = cost_matrix[0]
        put_after: float = cost_matrix[1]
        put_tied: float = cost_matrix[2]

        # if x should not be placed after y, then arc from x to y
        if put_before > put_after or put_before > put_tied:
            arcs.append((el_2, el_1))
        # if y should not be placed after x, then arc from y to x
        if put_after > put_before or put_after > put_tied:
            arcs.append((el_1, el_2))

    @staticmethod
    def can_be_all_tied(id_elements_to_check: Set[int], cost_matrix: ndarray) -> bool:
        """
        Check if all elements in a given set can be tied together with minimal cost.

        This method goes through all pairs of elements in the given set, checking the cost of tying them together.
        If the cost of tying any pair is higher than placing one before or after the other, the function returns False,
        indicating that not all elements in the set can be tied together with minimal cost.

        :param id_elements_to_check: a set of IDs of the elements to be checked.
        :type id_elements_to_check: Set[int]
        :param cost_matrix: a 3D matrix where cost_matrix[i][j][k] denotes the cost of placing i and j in
                            k-th relative position in the consensus.
        :type cost_matrix: ndarray
        :return: True if all elements can be tied together with minimal cost, False otherwise.
        :rtype: bool
        """
        if len(id_elements_to_check) < 2:
            return True
        for el_1, el_2 in combinations(id_elements_to_check, 2):
            cost_to_tie = cost_matrix[el_1][el_2][2]
            cost_to_place_before = cost_matrix[el_1][el_2][0]
            cost_to_place_after = cost_matrix[el_1][el_2][1]
            if cost_to_tie > min(cost_to_place_before, cost_to_place_after):
                return False
        return True
