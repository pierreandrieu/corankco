from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from typing import Tuple
from itertools import combinations
from numpy import vdot, ndarray, count_nonzero, shape, array, zeros, asarray
from igraph import Graph


class ParCons(MedianRanking):
    def __init__(self, auxiliary_algorithm=None, bound_for_exact=80):
        if isinstance(auxiliary_algorithm, MedianRanking):
            self.auxiliary_alg = auxiliary_algorithm
        else:
            self.auxiliary_alg = BioConsert(starting_algorithms=None)
        self.bound_for_exact = bound_for_exact

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
        if self.bound_for_exact > 0:
            from corankco.algorithms.exact.exactalgorithm import ExactAlgorithm

        optimal = True
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
        gr1, mat_score = self.__graph_of_elements(positions, sc)
        scc = gr1.components()
        for scc_i in scc:
            if len(scc_i) == 1:
                res.append([id_elements.get(scc_i[0])])
            else:
                all_tied = True
                for e1, e2 in combinations(scc_i, 2):
                    if mat_score[e1][e2][2] > mat_score[e1][e2][0] or mat_score[e1][e2][2] > mat_score[e1][e2][1]:
                        all_tied = False
                        break
                if all_tied:
                    buck = []
                    for el in scc_i:
                        buck.append(id_elements.get(el))
                    res.append(buck)
                else:
                    set_scc = set(scc_i)
                    project_rankings = []
                    for ranking in rankings:
                        project_ranking = []
                        for bucket in ranking:
                            project_bucket = []
                            for elem in bucket:
                                if elem_id.get(elem) in set_scc:
                                    project_bucket.append(elem)
                            if len(project_bucket) > 0:
                                project_ranking.append(project_bucket)
                        if len(project_ranking) > 0:
                            project_rankings.append(project_ranking)
                    if len(scc_i) > self.bound_for_exact:
                        cons_ext = self.auxiliary_alg.compute_consensus_rankings(Dataset(project_rankings),
                                                                                 scoring_scheme,
                                                                                 True).consensus_rankings[0]
                        res.extend(cons_ext)
                        optimal = False
                    else:
                        cons_ext = ExactAlgorithm(preprocess=False).compute_consensus_rankings(
                                                                            Dataset(project_rankings),
                                                                            scoring_scheme,
                                                                            True).consensus_rankings[0]
                        res.extend(cons_ext)
        hash_information = {ConsensusFeature.IsNecessarilyOptimal: optimal,
                            ConsensusFeature.AssociatedAlgorithm: self.get_full_name()
                            }
        if not bench_mode:
            cfc_name = []
            for scc_i in scc:
                group = set()
                for elem in scc_i:
                    group.add(id_elements[elem])
                cfc_name.append(group)
            hash_information[ConsensusFeature.WeakPartitioning] = cfc_name

        return Consensus(consensus_rankings=[res],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att=hash_information)

    @staticmethod
    def __graph_of_elements(positions: ndarray, matrix_scoring_scheme: ndarray) -> Tuple[Graph, ndarray]:
        graph_of_elements = Graph(directed=True)
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
                matrix[e1][e2] = [put_before, put_after, put_tied]
                matrix[e2][e1] = [put_after, put_before, put_tied]
        graph_of_elements.add_edges(edges)
        return graph_of_elements, matrix

    def get_full_name(self) -> str:
        return "ParCons, uses  \"" + self.auxiliary_alg.get_full_name() + "\" on groups of size >  " + str(self.bound_for_exact)

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        return True
