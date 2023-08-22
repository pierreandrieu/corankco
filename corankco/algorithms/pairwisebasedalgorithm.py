"""
Module that implements generic functions about pairwise based rank aggregation algorithm. Module for code factorisation.
"""

from typing import Tuple, Set
from itertools import combinations
from numba import jit
from igraph import Graph
from numpy import ndarray, shape, zeros, asarray, logical_or, where, logical_and, ones, column_stack, newaxis
from corankco.scoringscheme import ScoringScheme


@jit("float64[:, :, :](int32[:, :], float64[:, :], float64[:], int32, int32)", nopython=True, cache=True)
def _pairwise_cost_matrix_only(positions, scoring_scheme_numpy, weights, nb_elem, nb_rankings) -> ndarray:
    """
    Computes the pairwise cost matrix.

    :param positions: The 2D ndarray matrix where positions[i][j] is the position of element int id i in ranking j
    :param scoring_scheme_numpy: The associated scoring scheme, 2D numpy ndarray form.
    :param weights: a float64 array that associates a weight for each ranking
    :return: The pairwise cost matrix as n * n * 3 ndarray, where n is the number of elements
    """

    scoring_scheme_b_vector = scoring_scheme_numpy[0]
    scoring_scheme_t_vector = scoring_scheme_numpy[1]

    # create the matrix
    matrix = zeros((nb_elem, nb_elem, 3))

    # 2D float array, weighted_b_vector[i] = scoring_scheme_b_vector * weights[i]
    # dimension of the array: nb_rankings, 6
    weighted_b_vector = scoring_scheme_b_vector * weights[:, newaxis]
    # same for t vector
    weighted_t_vector = scoring_scheme_t_vector * weights[:, newaxis]

    # fill the matrix
    for elem1 in range(nb_elem):
        # array : pos of element 1 in all rankings
        all_pos_elem1 = positions[elem1]

        # pointer save
        cost_elem1 = matrix[elem1]
        for elem2 in range(elem1 + 1, nb_elem):
            # array : pos of element 2 in all rankings
            all_pos_elem2 = positions[elem2]

            cost_elem1_elem2 = cost_elem1[elem2]
            for id_ranking in range(nb_rankings):
                # pos of element 1 in ranking id_ranking
                pos_elem1 = all_pos_elem1[id_ranking]
                # pos of element 2 in ranking id_ranking
                pos_elem2 = all_pos_elem2[id_ranking]

                # if both elements are ranked in the target ranking
                if pos_elem1 != -1 and pos_elem2 != -1:
                    # elem1 before elem2
                    if pos_elem1 < pos_elem2:
                        cost_elem1_elem2[0] += weighted_b_vector[id_ranking][0]
                        cost_elem1_elem2[1] += weighted_b_vector[id_ranking][1]
                        cost_elem1_elem2[2] += weighted_t_vector[id_ranking][0]

                    # elem2 before elem1
                    elif pos_elem1 > pos_elem2:
                        cost_elem1_elem2[0] += weighted_b_vector[id_ranking][1]
                        cost_elem1_elem2[1] += weighted_b_vector[id_ranking][0]
                        cost_elem1_elem2[2] += weighted_t_vector[id_ranking][1]

                    # elem1 tied with elem2
                    else:
                        cost_elem1_elem2[0] += weighted_b_vector[id_ranking][2]
                        cost_elem1_elem2[1] += weighted_b_vector[id_ranking][2]
                        cost_elem1_elem2[2] += weighted_t_vector[id_ranking][2]
                # only elem1 is ranked
                elif pos_elem1 != -1:
                    cost_elem1_elem2[0] += weighted_b_vector[id_ranking][3]
                    cost_elem1_elem2[1] += weighted_b_vector[id_ranking][4]
                    cost_elem1_elem2[2] += weighted_t_vector[id_ranking][3]

                # only elem2 is ranked
                elif pos_elem2 != -1:
                    cost_elem1_elem2[0] += weighted_b_vector[id_ranking][4]
                    cost_elem1_elem2[1] += weighted_b_vector[id_ranking][3]
                    cost_elem1_elem2[2] += weighted_t_vector[id_ranking][4]

                # elem1 and elem2 are non-ranked
                else:
                    cost_elem1_elem2[0] += weighted_b_vector[id_ranking][5]
                    cost_elem1_elem2[1] += weighted_b_vector[id_ranking][5]
                    cost_elem1_elem2[2] += weighted_t_vector[id_ranking][5]

            # matrix is symmetric
            matrix[elem2][elem1][0] = cost_elem1_elem2[1]
            matrix[elem2][elem1][1] = cost_elem1_elem2[0]
            matrix[elem2][elem1][2] = cost_elem1_elem2[2]

    return matrix


class PairwiseBasedAlgorithm:
    """

    Class to gather several useful methods for pairwise based algorithms. Class for code factorisation.
    """

    @staticmethod
    def graph_of_elements_with_robust_arcs(positions: ndarray, scoring_scheme: ScoringScheme,
                                           weights: ndarray = None) -> Tuple[Graph, ndarray, Set[Tuple[int, int]]]:
        """
        Compute the graph of elements, the cost of pairwise relative positions and the set of robust arcs defined in the
        Future Generation Computer Systems article (as mentioned in the Class docstring)

        This function generates a graph of elements as defined in the Future Generation Computer Systems article
        (as mentioned in the Class docstring) and computes the cost of pairwise relative positions.
        The latter is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        i after j, i tied with j in the consensus according to the scoring scheme.

        :param positions: a matrix where pos[i][j] denotes the position of element i in ranking j (-1 if non-ranked)
        :param scoring_scheme: the scoring scheme to compute the cost matrix
        :param weights: a 1D float array that associates a weight for each ranking
        :return: A tuple containing the Graph of elements defined in the FGCS article, the 3D matrix of costs of
        pairwise relative positions, and the set of the robust arcs defined in the FGCS article
        """
        if weights is None:
            weights = ones(positions.shape[1], dtype=float)
        assert weights.shape[0] == positions.shape[1]
        pairwise_matrix: ndarray = PairwiseBasedAlgorithm.pairwise_cost_matrix(positions, scoring_scheme, weights)
        return (PairwiseBasedAlgorithm._get_graph_of_elements_from_matrix(pairwise_matrix),
                pairwise_matrix,
                PairwiseBasedAlgorithm._get_robust_arcs_from_matrix(pairwise_matrix))

    @staticmethod
    def graph_of_elements(positions: ndarray, scoring_scheme: ScoringScheme,
                          weights: ndarray = None) -> Tuple[Graph, ndarray]:
        """
        Compute the graph of elements, the cost of pairwise relative positions and the set of robust arcs defined in the
        Future Generation Computer Systems article (as mentioned in the Class docstring)

        This function generates a graph of elements as defined in the Future Generation Computer Systems article
        (as mentioned in the Class docstring) and computes the cost of pairwise relative positions.
        The latter is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        i after j, i tied with j in the consensus according to the scoring scheme.

        :param positions: a matrix where pos[i][j] denotes the position of element i in ranking j (-1 if non-ranked)
        :param scoring_scheme: the Scoring Scheme to compute the cost matrix
        :param weights: a 1D float array that associates a weight for each ranking
        :return: A tuple containing the Graph of elements defined in the FGCS article, the 3D matrix of costs of
        pairwise relative positions
        """
        if weights is None:
            weights = ones(positions.shape[1], dtype=float)
        assert weights.shape[0] == positions.shape[1]

        pairwise_matrix: ndarray = PairwiseBasedAlgorithm.pairwise_cost_matrix(positions, scoring_scheme, weights)
        return PairwiseBasedAlgorithm._get_graph_of_elements_from_matrix(pairwise_matrix), pairwise_matrix

    @staticmethod
    def pairwise_cost_matrix(positions: ndarray, scoring_scheme: ScoringScheme, weights: ndarray = None) -> ndarray:
        """
        Compute the cost of pairwise relative positions.

        This function computes the cost of pairwise relative positions.
        The latter is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        i after j, i tied with j in the consensus according to the scoring scheme.

        :param positions: a matrix where pos[i][j] denotes the position of element i in ranking j (-1 if non-ranked)
        :param scoring_scheme: the scoring scheme to compute the cost matrix
        :param weights: a 1D float array that associates a weight for each ranking
        :return: The 3D matrix of costs of pairwise relative positions.
        """
        if weights is None:
            weights = ones(positions.shape[1], dtype=float)
        assert weights.shape[0] == positions.shape[1]
        nb_elem = positions.shape[0]
        nb_rankings = positions.shape[1]
        return _pairwise_cost_matrix_only(positions, asarray(scoring_scheme.penalty_vectors),
                                          weights, nb_elem, nb_rankings)

    @staticmethod
    def _get_robust_arcs_from_matrix(matrix: ndarray) -> Set[Tuple[int, int]]:
        # pairs i,j where matrix[i][j][1] > matrix[i, j, 0] i.e. i before j cheaper than i after j
        before_cheaper_after = matrix[:, :, 1] > matrix[:, :, 0]
        # pairs i,j where matrix[i][j][2] > matrix[i, j, 0] i.e. i before j cheaper than i tied with j
        before_cheaper_tied = matrix[:, :, 2] > matrix[:, :, 0]

        return {(elem1, elem2) for elem1, elem2 in
                column_stack(where(logical_and(before_cheaper_after, before_cheaper_tied)))}

    @staticmethod
    def _get_graph_of_elements_from_matrix(matrix: ndarray) -> Graph:
        graph_of_elements: Graph = Graph(directed=True)

        # add a vertex for each element
        for i in range(shape(matrix)[0]):
            graph_of_elements.add_vertex(name=str(i))

        # pairs i,j where matrix[i][j][1] > matrix[i, j, 0] i.e. i before j cheaper than i after j
        before_cheaper_after = matrix[:, :, 1] > matrix[:, :, 0]
        # pairs i,j where matrix[i][j][1] > matrix[i, j, 2] i.e. i tied with j cheaper than i after j
        tied_cheaper_after = matrix[:, :, 1] > matrix[:, :, 2]
        after_not_cheapest = logical_or(before_cheaper_after, tied_cheaper_after)
        # arcs of the graph: pairs (i, j) where cost of i after j is not the cheapest
        # arcs should be added all at once, the impact on performances is clear
        graph_of_elements.add_edges(list(column_stack(where(after_not_cheapest))))

        return graph_of_elements

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
