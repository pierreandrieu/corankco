from typing import Tuple, List
from igraph import Graph
from numpy import vdot, ndarray, count_nonzero, shape, array, zeros
from typing import Set
from itertools import combinations


class PairwiseBasedAlgorithm:
    """

    Class to gather several useful methods for pairwise based algorithms. Class for code factorisation.
    """
    @staticmethod
    def graph_of_elements(positions: ndarray, matrix_scoring_scheme: ndarray) -> \
            Tuple[Graph, ndarray, Set[Tuple[int, int]]]:
        """
        Compute the graph of elements, the cost of pairwise relative positions and the set of robust arcs defined in the
        Future Generation Computer Systems article (as mentioned in the Class docstring)

        This function generates a graph of elements as defined in the Future Generation Computer Systems article
        (as mentioned in the Class docstring) and computes the cost of pairwise relative positions.
        The latter is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        i after j, i tied with j in the consensus according to the scoring scheme.

        :param positions: a matrix where pos[i][j] denotes the position of element i in ranking j (-1 if non-ranked)
        :param matrix_scoring_scheme: the numpy ndarray version of the scoring scheme
        :return: A tuple containing the Graph of elements defined in the FGCS article, the 3D matrix of costs of
        pairwise relative positions, and the set of the robust arcs defined in the FGCS article
        """
        graph_of_elements: Graph = Graph(directed=True)
        robust_arcs: Set[Tuple[int, int]] = set()

        cost_before: ndarray = matrix_scoring_scheme[0]
        cost_tied: ndarray = matrix_scoring_scheme[1]
        cost_after: ndarray = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                                     cost_before[5]])


        # n = nb of elements, m = nb of rankings
        n: int = shape(positions)[0]
        m: int = shape(positions)[1]

        # add a vertex for each element
        for i in range(n):
            graph_of_elements.add_vertex(name=str(i))

        # matrix[i][j] contains the costs of the 3 possible relative orderings between i and j
        # matrix[i][j][0] = cost to place i before j, [1] = cost to place i after j, [2] = cost to tie i and j
        matrix: ndarray = zeros((n, n, 3))

        # arcs to add in the graph. There is an arc from x to y in the graph of elements iif the cost to place
        # y before x in the consensus is NOT minimal. Intuitively, an arc from x to y mean "not after"
        arcs: List[Tuple[int, int]] = []

        for e1 in range(n):
            # memoization: the positions of e1 in the input rankings
            mem: ndarray = positions[e1]

            # d = number of input rankings such that e1 is non-ranked
            d: int = count_nonzero(mem == -1)

            for e2 in range(e1 + 1, n):
                # a : nb of input rankings such that e1 and e2 both non-ranked
                a: int = count_nonzero(mem + positions[e2] == -2)
                # b = nb of input rankings such that e1 and e2 have same position, or both non-ranked
                b: int = count_nonzero(mem == positions[e2])
                # c = nb of input rankings such that e2 is non-ranked
                c: int = count_nonzero(positions[e2] == -1)
                # e = nb of input rankings such that e1 < e2 or e1 is non-ranked
                e: int = count_nonzero(mem < positions[e2])

                # vector that contains for the two elements x and y the number of rankings such that respectively:
                # x < y, x > y, x and y are tied, x is the only ranked, y is the only ranked, x and y are non-ranked
                relative_positions: ndarray = array([e - d + a, m - e - b - c + a, b - a, c - a, d - a, a])

                # cost to place e1 before, after, or tied with e2 in a consensus ranking within a Kemeny prism
                put_before: float = vdot(relative_positions, cost_before)
                put_after: float = vdot(relative_positions, cost_after)
                put_tied: float = vdot(relative_positions, cost_tied)

                # if x should not be placed after y, then arc from x to y
                if put_before > put_after or put_before > put_tied:
                    arcs.append((e2, e1))
                # if y should not be placed after x, then arc from y to x
                if put_after > put_before or put_after > put_tied:
                    arcs.append((e1, e2))

                if put_before < put_after and put_before < put_tied:
                    robust_arcs.add((e1, e2))
                if put_after < put_before and put_after < put_tied:
                    robust_arcs.add((e2, e1))

                # save the costs, will be used further
                matrix[e1][e2] = [put_before, put_after, put_tied]
                matrix[e2][e1] = [put_after, put_before, put_tied]

        # arcs should be added all at once, the impact on performances is clear
        graph_of_elements.add_edges(arcs)
        return graph_of_elements, matrix, robust_arcs

    @staticmethod
    def pairwise_cost_matrix(positions: ndarray, matrix_scoring_scheme: ndarray) -> ndarray:
        """
        Compute the graph of elements and the cost of pairwise relative positions.

        This function generates a graph of elements as defined in the Future Generation Computer Systems article
        (as mentioned in the Class docstring) and computes the cost of pairwise relative positions.
        The latter is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        i after j, i tied with j in the consensus according to the scoring scheme.

        :param positions: a matrix where pos[i][j] denotes the position of element i in ranking j (-1 if non-ranked)
        :param matrix_scoring_scheme: the numpy ndarray version of the scoring scheme
        :return: A tuple containing the Graph of elements defined in the FGCS article and the 3D matrix of costs of
        pairwise relative positions.
        """
        cost_before: ndarray = matrix_scoring_scheme[0]
        cost_tied: ndarray = matrix_scoring_scheme[1]
        cost_after: ndarray = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                                     cost_before[5]])

        # n = nb of elements, m = nb of rankings
        n: int = shape(positions)[0]
        m: int = shape(positions)[1]

        # matrix[i][j] contains the costs of the 3 possible relative orderings between i and j
        # matrix[i][j][0] = cost to place i before j, [1] = cost to place i after j, [2] = cost to tie i and j
        matrix: ndarray = zeros((n, n, 3))

        # arcs to add in the graph. There is an arc from x to y in the graph of elements iif the cost to place
        # y before x in the consensus is NOT minimal. Intuitively, an arc from x to y mean "not after"
        arcs: List[Tuple[int, int]] = []

        for e1 in range(n):
            # memoization: the positions of e1 in the input rankings
            mem: ndarray = positions[e1]

            # d = number of input rankings such that e1 is non-ranked
            d: int = count_nonzero(mem == -1)

            for e2 in range(e1 + 1, n):
                # a : nb of input rankings such that e1 and e2 both non-ranked
                a: int = count_nonzero(mem + positions[e2] == -2)
                # b = nb of input rankings such that e1 and e2 have same position, or both non-ranked
                b: int = count_nonzero(mem == positions[e2])
                # c = nb of input rankings such that e2 is non-ranked
                c: int = count_nonzero(positions[e2] == -1)
                # e = nb of input rankings such that e1 < e2 or e1 is non-ranked
                e: int = count_nonzero(mem < positions[e2])

                # vector that contains for the two elements x and y the number of rankings such that respectively:
                # x < y, x > y, x and y are tied, x is the only ranked, y is the only ranked, x and y are non-ranked
                relative_positions: ndarray = array([e - d + a, m - e - b - c + a, b - a, c - a, d - a, a])

                # cost to place e1 before, after, or tied with e2 in a consensus ranking within a Kemeny prism
                put_before: float = vdot(relative_positions, cost_before)
                put_after: float = vdot(relative_positions, cost_after)
                put_tied: float = vdot(relative_positions, cost_tied)

                # save the costs, will be used further
                matrix[e1][e2] = [put_before, put_after, put_tied]
                matrix[e2][e1] = [put_after, put_before, put_tied]
        return matrix

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
        for e1, e2 in combinations(id_elements_to_check, 2):
            cost_to_tie = cost_matrix[e1][e2][2]
            cost_to_place_before = cost_matrix[e1][e2][0]
            cost_to_place_after = cost_matrix[e1][e2][1]
            if cost_to_tie > min(cost_to_place_before, cost_to_place_after):
                return False
        return True
