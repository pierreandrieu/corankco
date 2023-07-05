from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from typing import Tuple, List, Set, Dict
from itertools import combinations
from igraph import Graph, VertexClustering
from corankco.element import Element
from numpy import vdot, ndarray, count_nonzero, shape, array, zeros, asarray
from corankco.ranking import Ranking


class ParCons(MedianRanking):
    """
    ParCons is a graph-based heuristics for Kemeny-Young rank aggregation published in P. Andrieu, B. Brancotte,
    L. Bulteau, S. Cohen-Boulakia, A. Denise, A. Pierrot, S. Vialette, Efficient, robust and effective rank aggregation
    for massive biological datasets, Future Generation Computer Systems, 2021, pp 406–421.
    Complexity: O(nb_elements² * nb_rankings)
    ParCons divides the initial problem into subproblems such that concatenating an optimal solutions of each subproblem
    forms an optimal solution for the initial problem.
    If the size of a given subproblem is <= 80 elements (can be modified), the exact algorithm is run
    If the size of a given subproblem is > 80 elements, another algorithm, given as attribute of the instance, is run
    to get a consensus for the subproblem.
    Note that this heuristics may be aware of having an optimal solution. If no auxiliary heuristics has been used for a
    given instance, the returned consensus is necessarily optimal.
    """
    def __init__(self, auxiliary_algorithm: MedianRanking = None, bound_for_exact=80):
        """
        Construct a ParCons instance
        :param auxiliary_algorithm: the rank aggregation algorithm (MedianRanking instance) to use for
        subproblems whose number of elements is greater than the attribute "bound_for_exact". Default is BioConsert
        :param bound_for_exact: the maximal number of elements for a given sub-problem such that the exact algorithm
        will be used to get a consensus of the sub-problem
        """
        if isinstance(auxiliary_algorithm, MedianRanking):
            self._auxiliary_alg: MedianRanking = auxiliary_algorithm
        else:
            self._auxiliary_alg: MedianRanking = BioConsert(starting_algorithms=None)
        self._bound_for_exact: int = bound_for_exact

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking=False,
            bench_mode=False
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
        :rtype: Consensus
        :raise ScoringSchemeNotHandledException: When the algorithm cannot compute the consensus because the
        implementation does not support the given scoring scheme.
        """

        # prevent circular inclusions
        if self._bound_for_exact > 0:
            from corankco.algorithms.exact.exactalgorithm import ExactAlgorithm

        # optimal unless a non-exact auxiliary algorithm is used
        optimal: bool = True

        # numpy version of scoring scheme
        sc: ndarray = asarray(scoring_scheme.penalty_vectors)

        rankings: List[Ranking] = dataset.rankings
        res: List[Set[Element]] = []

        # mappings between elements and int IDs
        elem_id: Dict[Element, int] = dataset.mapping_elem_id
        id_elements: Dict[int, Element] = dataset.mapping_id_elem

        # positions[i][j] = position of element of id i in ranking j, -1 if non-ranked
        positions: ndarray = dataset.get_positions()

        # get the graph of elements and the cost matrix
        gr1, mat_score = self.__graph_of_elements(positions, sc)

        # get the strongly connected components in a topological sort
        scc: VertexClustering = gr1.components()
        
        # for each SCC (defining a sub-problem)
        for scc_i in scc:
            # if scc = single element, the solution is trivial, a bucket with this element is added in the consensus
            if len(scc_i) == 1:
                bucket: Set[Element] = {id_elements.get(scc_i[0])}
                res.append(bucket)
            else:
                # if scc has several elements but all pairs have tied cost as minimal cost,
                # a trivial solution is to tie them in the consensus: a bucket containing all these elements is added
                all_tied = True
                for e1, e2 in combinations(scc_i, 2):
                    if mat_score[e1][e2][2] > mat_score[e1][e2][0] or mat_score[e1][e2][2] > mat_score[e1][e2][1]:
                        all_tied = False
                        break
                if all_tied:
                    buck: Set[Element] = set()
                    for el in scc_i:
                        buck.add(id_elements.get(el))
                    res.append(buck)

                # if there is at least one pair of elements that cannot be tied with minimal cost,
                # then we have no trivial optimal solution. According to the size of the sub-problem, use of
                # the exact algorithm or a heuristics
                else:
                    # creation of a new Dataset representing the sub-problem
                    set_scc = set(scc_i)
                    project_rankings: List[Ranking] = []
                    for ranking in rankings:
                        project_ranking: List[Set[Element]] = []
                        for bucket in ranking:
                            project_bucket: Set[Element] = set(elem for elem in bucket if elem_id[elem] in set_scc)
                            if len(project_bucket) > 0:
                                project_ranking.append(project_bucket)
                        if len(project_ranking) > 0:
                            project_rankings.append(Ranking(project_ranking))
                    if len(scc_i) > self._bound_for_exact:
                        cons_ext = self._auxiliary_alg.compute_consensus_rankings(Dataset(project_rankings),
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
            hash_information[ConsensusFeature.WeakPartitioning] = [set(scc_i) for scc_i in scc]

        return Consensus(consensus_rankings=[Ranking(res)],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att=hash_information)

    @staticmethod
    def __graph_of_elements(positions: ndarray, matrix_scoring_scheme: ndarray) -> Tuple[Graph, ndarray]:
        graph_of_elements: Graph = Graph(directed=True)
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
        edges = []

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
                    edges.append((e2, e1))
                # if y should not be placed after x, then arc from y to x
                if put_after > put_before or put_after > put_tied:
                    edges.append((e1, e2))

                # save the costs, will be used further
                matrix[e1][e2] = [put_before, put_after, put_tied]
                matrix[e2][e1] = [put_after, put_before, put_tied]
        graph_of_elements.add_edges(edges)
        return graph_of_elements, matrix

    def get_full_name(self) -> str:
        return "ParCons, uses  \"" + self._auxiliary_alg.get_full_name() + "\" on groups of size >  " + \
            str(self._bound_for_exact)

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        return True
