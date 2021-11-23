from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from typing import Tuple, List, Set
from numpy import vdot, ndarray, count_nonzero, shape, array, zeros, asarray
from igraph import Graph


class ParFront:

    def __init__(self):
        pass

    def compute_frontiers(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme
    ) -> List[Set]:
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The penalty vectors to consider
        :type scoring_scheme: ScoringScheme (class ScoringScheme in package 'distances')
        :return a list of sets of elements such that any exact consensus respects this partitioning
        """
        sc = asarray(scoring_scheme.penalty_vectors)
        rankings = dataset.rankings
        res = []
        elem_id = {}
        id_elements = {}
        id_elem = 0
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if element not in elem_id:
                        elem_id[element] = id_elem
                        id_elements[id_elem] = element
                        id_elem += 1

        positions = dataset.get_positions(elem_id)
        gr1, mat_score, robust_arcs = self.__graph_of_elements(positions, sc)
        sccs = gr1.components()
        partition = []
        for scc in sccs:
            partition.append(set(scc))
        i = 0
        while i < len(partition) - 1:
            set1 = partition[i]
            set2 = partition[i+1]
            fusion = False
            for x in set1:
                for y in set2:
                    if (x, y) not in robust_arcs:
                        fusion = True
                        break
                if fusion:
                    break
            if fusion:
                for x in set2:
                    set1.add(x)
                partition.pop(i+1)
                i = max(i-1, 1)
            else:
                i += 1

        res = []
        for group in partition:
            g = set()
            res.append(g)
            for elem in group:
                g.add(id_elements[elem])
        return res

    @staticmethod
    def __graph_of_elements(positions: ndarray, matrix_scoring_scheme: ndarray) -> Tuple[Graph, ndarray, Set[Tuple]]:
        graph_of_elements = Graph(directed=True)
        robust_arcs = set()
        cost_before = matrix_scoring_scheme[0]
        cost_tied = matrix_scoring_scheme[1]
        cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                            cost_before[5]])
        n = shape(positions)[0]
        m = shape(positions)[1]
        for i in range(n):
            graph_of_elements.add_vertex(name=str(i))

        matrix = zeros((n, n, 3))
        edges = []
        for e1 in range(n):
            mem = positions[e1]
            d = count_nonzero(mem == -1)
            for e2 in range(e1 + 1, n):
                a = count_nonzero(mem + positions[e2] == -2)
                b = count_nonzero(mem == positions[e2])
                c = count_nonzero(positions[e2] == -1)
                e = count_nonzero(mem < positions[e2])
                relative_positions = array([e - d + a, m - e - b - c + a, b - a, c - a, d - a, a])
                put_before = vdot(relative_positions, cost_before)
                put_after = vdot(relative_positions, cost_after)
                put_tied = vdot(relative_positions, cost_tied)
                if put_before > put_after or put_before > put_tied:
                    edges.append((e2, e1))
                if put_after > put_before or put_after > put_tied:
                    edges.append((e1, e2))
                if put_before < put_after and put_before < put_tied:
                    robust_arcs.add((e1, e2))
                if put_after < put_before and put_after < put_tied:
                    robust_arcs.add((e2, e1))
                matrix[e1][e2] = [put_before, put_after, put_tied]
                matrix[e2][e1] = [put_after, put_before, put_tied]
        graph_of_elements.add_edges(edges)
        return graph_of_elements, matrix, robust_arcs
