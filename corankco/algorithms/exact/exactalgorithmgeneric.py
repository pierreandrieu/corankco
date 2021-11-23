from typing import List, Dict, Tuple, Set
from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from numpy import ndarray, array, shape, zeros, count_nonzero, vdot, asarray
from operator import itemgetter
import pulp
from igraph import Graph


class ExactAlgorithmGeneric(MedianRanking):
    def __init__(self):
        pass

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking=False,
            bench_mode=False
    ) -> Consensus:
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The penalty vectors to consider
        :type scoring_scheme: ScoringScheme (class ScoringScheme in package 'distances')
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :param bench_mode: is bench mode activated. If False, the algorithm may return more information
        :type bench_mode: bool
        :return one or more rankings if the underlying algorithm can find several equivalent consensus rankings
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found.
        In all scenario, the algorithm returns a list of consensus rankings
        :raise ScoringSchemeNotHandledException when the algorithm cannot compute the consensus because the
        implementation of the algorithm does not fit with the scoring scheme
        """
        rankings = dataset.rankings
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
        nb_elem = len(elem_id)

        positions = ExactAlgorithmGeneric.__positions(rankings, elem_id)

        sc = asarray(scoring_scheme.penalty_vectors)

        graph, mat_score, ties_must_be_checked = self.__graph_of_elements(positions, sc)

        my_values = []
        my_vars = []

        h_vars = {}
        cpt = 0

        for i in range(nb_elem):
            for j in range(nb_elem):
                if not i == j:
                    name_var = "x_%s_%s" % (i, j)
                    my_values.append(mat_score[i][j][0])
                    my_vars.append(pulp.LpVariable(name_var, 0, 1, cat="Binary"))
                    h_vars[name_var] = cpt
                    cpt += 1
                    if i < j:
                        name_var = "t_%s_%s" % (i, j)
                        my_values.append(mat_score[i][j][2])
                        my_vars.append(pulp.LpVariable(name_var, 0, 1, cat="Binary"))
                        h_vars[name_var] = cpt
                        cpt += 1

        prob = pulp.LpProblem("myProblem", pulp.LpMinimize)

        # add the binary order constraints
        for i in range(0, nb_elem - 1):
            for j in range(i + 1, nb_elem):
                if not i == j:
                    prob += my_vars[h_vars["x_%s_%s" % (i, j)]] \
                            + my_vars[h_vars["x_%s_%s" % (j, i)]] \
                            + my_vars[h_vars["t_%s_%s" % (i, j)]] == 1

        # add the transitivity constraints
        for i in range(0, nb_elem):
            for j in range(nb_elem):
                if j != i:
                    i_bef_j = "x_%s_%s" % (i, j)
                    if i < j:
                        i_tie_j = "t_%s_%s" % (i, j)
                    else:
                        i_tie_j = "t_%s_%s" % (j, i)
                    for k in range(nb_elem):
                        if k != i and k != j:
                            j_bef_k = "x_%s_%s" % (j, k)
                            i_bef_k = "x_%s_%s" % (i, k)
                            if j < k:
                                j_tie_k = "t_%s_%s" % (j, k)
                            else:
                                j_tie_k = "t_%s_%s" % (k, j)

                            if i < k:
                                i_tie_k = "t_%s_%s" % (i, k)
                            else:
                                i_tie_k = "t_%s_%s" % (k, i)

                            prob += my_vars[h_vars[i_bef_j]] +\
                                my_vars[h_vars[j_bef_k]] \
                                + my_vars[h_vars[j_tie_k]] \
                                - my_vars[h_vars[i_bef_k]] <= 1

                            prob += my_vars[h_vars[i_bef_j]] + \
                                my_vars[h_vars[i_tie_j]] \
                                + my_vars[h_vars[j_bef_k]] - my_vars[h_vars[i_bef_k]] <= 1

                            prob += 2 * my_vars[h_vars[i_tie_j]] \
                                + 2 * my_vars[h_vars[j_tie_k]] \
                                - my_vars[h_vars[i_tie_k]] <= 3

        # optimization
        if not ties_must_be_checked:
            for i in range(0, nb_elem - 1):
                for j in range(i + 1, nb_elem):
                    if not i == j:
                        prob += my_vars[h_vars["t_%s_%s" % (i, j)]] == 0

        cfc = graph.components()

        for i in range(len(cfc)):
            group_i = cfc[i]
            for j in range(i+1, len(cfc)):
                for elem_i in group_i:
                    for elem_j in cfc[j]:
                        prob += my_vars[h_vars["x_%s_%s" % (elem_i, elem_j)]] == 1
                        prob += my_vars[h_vars["x_%s_%s" % (elem_j, elem_i)]] == 0
                        if elem_i < elem_j:
                            prob += my_vars[h_vars["t_%s_%s" % (elem_i, elem_j)]] == 0
                        else:
                            prob += my_vars[h_vars["t_%s_%s" % (elem_j, elem_i)]] == 0

        # objective function
        prob += pulp.lpSum(my_vars[cpt] * my_values[cpt] for cpt in range(len(my_vars)))

        try:
            prob.solve(pulp.CPLEX(msg=False))
        except:
            prob.solve(pulp.PULP_CBC_CMD(msg=False))

        h_def = {i: 0 for i in range(nb_elem)}

        for var in my_vars:
            if abs(var.value() - 1) < 0.01 and var.name[0] == "x":
                h_def[int(var.name.split("_")[2])] += 1

        ranking = []
        current_nb_def = 0
        bucket = []

        for elem, nb_defeats in (sorted(h_def.items(), key=itemgetter(1))):
            if nb_defeats == current_nb_def:
                bucket.append(id_elements[elem])
            else:
                ranking.append(bucket)
                bucket = [id_elements[elem]]
                current_nb_def = nb_defeats
        ranking.append(bucket)
        return Consensus(consensus_rankings=[ranking],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={ConsensusFeature.IsNecessarilyOptimal: True,
                              ConsensusFeature.KemenyScore: prob.objective.value(),
                              ConsensusFeature.AssociatedAlgorithm: self.get_full_name()
                              })

    @staticmethod
    def __graph_of_elements(positions: ndarray, matrix_scoring_scheme: ndarray) -> Tuple[Graph, ndarray, bool]:
        graph_of_elements = Graph(directed=True)
        cost_before = matrix_scoring_scheme[0]
        cost_tied = matrix_scoring_scheme[1]
        cost_after = array([cost_before[1], cost_before[0], cost_before[2], cost_before[4], cost_before[3],
                            cost_before[5]])
        n = shape(positions)[0]
        m = shape(positions)[1]
        ties_must_be_checked = False

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
                if 2 * put_tied <= (put_after + put_before):
                    ties_must_be_checked = True
                matrix[e1][e2] = [put_before, put_after, put_tied]
                matrix[e2][e1] = [put_after, put_before, put_tied]
        graph_of_elements.add_edges(edges)
        return graph_of_elements, matrix, ties_must_be_checked

    @staticmethod
    def __positions(rankings: List[List[List or Set[int or str]]], elements_id: Dict) -> ndarray:
        positions = zeros((len(elements_id), len(rankings)), dtype=int) - 1
        id_ranking = 0
        for ranking in rankings:
            id_bucket = 0
            for bucket in ranking:
                for element in bucket:
                    positions[elements_id.get(element)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def get_full_name(self) -> str:
        return "Exact algorithm ILP pulp"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        return True
