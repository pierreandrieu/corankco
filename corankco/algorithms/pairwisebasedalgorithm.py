"""
Module that implements generic functions about pairwise based rank aggregation algorithm. Module for code factorisation.
"""

from typing import Tuple, List, Callable, Any, Set
from itertools import combinations
from igraph import Graph
from numpy import vdot, ndarray, count_nonzero, shape, array, zeros, asarray
from corankco.scoringscheme import ScoringScheme


class PairwiseBasedAlgorithm:
    """

    Class to gather several useful methods for pairwise based algorithms. Class for code factorisation.
    """

    @staticmethod
    def pairwise_cost_matrix_generic(positions: ndarray,
                                     scoring_scheme: ScoringScheme,
                                     callback: Callable[[ndarray, int, int, Any], Any],
                                     structure: Any
                                     ) -> ndarray:
        """
        Computes the pairwise cost matrix, and allows for calling a function for each pair of elements after computing
        the cost of the different relative positions. Useful for code factorisation.

        :param positions: The 2D ndarray matrix where positions[i][j] is the position of element int id i in ranking j
        :param scoring_scheme: The associated scoring scheme.
        :param callback: The function to call after computing before(x,y), before(y,x), tied(x,y)
        :param structure: A structure object, a parameter for the callback function.
        :return: The pairwise cost matrix as n * n * 3 ndarray, where n is the number of elements
        """

        cost_before: ndarray = asarray(scoring_scheme.b_vector)
        cost_tied: ndarray = asarray(scoring_scheme.t_vector)
        cost_after: ndarray = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                                     cost_before[5]])

        # n = nb of elements, m = nb of rankings
        nb_elem: int = shape(positions)[0]
        nb_rankings: int = shape(positions)[1]

        # matrix[i][j] contains the costs of the 3 possible relative orderings between i and j
        # matrix[i][j][0] = cost to place i before j, [1] = cost to place i after j, [2] = cost to tie i and j
        matrix: ndarray = zeros((nb_elem, nb_elem, 3))

        for el_1 in range(nb_elem):
            # memoization: the positions of e1 in the input rankings
            mem: ndarray = positions[el_1]

            # d = number of input rankings such that e1 is non-ranked
            e1_non_ranked: int = count_nonzero(mem == -1)

            for el_2 in range(el_1 + 1, nb_elem):
                # nb of input rankings such that e1 and e2 both non-ranked
                e1_e2_non_ranked: int = count_nonzero(mem + positions[el_2] == -2)
                # nb of input rankings such that e1 and e2 have same position, or both non-ranked
                e1_e2_same_pos: int = count_nonzero(mem == positions[el_2])
                # nb of input rankings such that e2 is non-ranked
                e2_non_ranked: int = count_nonzero(positions[el_2] == -1)
                # nb of input rankings such that e1 < e2 or e1 is non-ranked
                e1_bef_e2_or_missing: int = count_nonzero(mem < positions[el_2])

                # vector that contains for the two elements x and y the number of rankings such that respectively:
                # x < y, x > y, x and y are tied, x is the only ranked, y is the only ranked, x and y are non-ranked
                relative_positions: ndarray = array([e1_bef_e2_or_missing - e1_non_ranked + e1_e2_non_ranked,
                                                     nb_rankings - e1_bef_e2_or_missing - e1_e2_same_pos - e2_non_ranked
                                                     + e1_e2_non_ranked,
                                                     e1_e2_same_pos - e1_e2_non_ranked,
                                                     e2_non_ranked - e1_e2_non_ranked,
                                                     e1_non_ranked - e1_e2_non_ranked,
                                                     e1_e2_non_ranked])

                # cost to place e1 before, after, or tied with e2 in a consensus ranking within a Kemeny prism
                put_before: float = float(vdot(relative_positions, cost_before))
                put_after: float = float(vdot(relative_positions, cost_after))
                put_tied: float = float(vdot(relative_positions, cost_tied))
                # save the costs, will be used further
                matrix[el_1][el_2] = [put_before, put_after, put_tied]
                matrix[el_2][el_1] = [put_after, put_before, put_tied]
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

        matrix: ndarray = PairwiseBasedAlgorithm.pairwise_cost_matrix_generic(
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

        matrix: ndarray = PairwiseBasedAlgorithm.pairwise_cost_matrix_generic(
            positions, scoring_scheme, PairwiseBasedAlgorithm._fill_graph, arcs)

        # arcs should be added all at once, the impact on performances is clear
        graph_of_elements.add_edges(arcs)
        return graph_of_elements, matrix

    @staticmethod
    def pairwise_cost_matrix(positions: ndarray, scoring_scheme: ScoringScheme) -> ndarray:
        """
        Compute the graph of elements and the cost of pairwise relative positions.

        This function generates a graph of elements as defined in the Future Generation Computer Systems article
        (as mentioned in the Class docstring) and computes the cost of pairwise relative positions.
        The latter is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        i after j, i tied with j in the consensus according to the scoring scheme.

        :param positions: a matrix where pos[i][j] denotes the position of element i in ranking j (-1 if non-ranked)
        :param scoring_scheme: the scoring scheme to compute the cost matrix
        :return: A tuple containing the Graph of elements defined in the FGCS article and the 3D matrix of costs of
        pairwise relative positions.
        """
        return PairwiseBasedAlgorithm.pairwise_cost_matrix_generic(
            positions, scoring_scheme, PairwiseBasedAlgorithm._nothing_to_do, None)

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
