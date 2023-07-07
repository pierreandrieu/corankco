from corankco.algorithms.median_ranking import MedianRanking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from typing import List, Set
from itertools import combinations
from igraph import VertexClustering
from corankco.element import Element
from numpy import ndarray, asarray
from corankco.ranking import Ranking
from corankco.algorithms.graphbasedalgorithm import GraphBasedAlgorithm


class ParCons(GraphBasedAlgorithm):
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
    DEFAULT_BOUND_FOR_EXACT = 80

    def __init__(self, auxiliary_algorithm: MedianRanking = None, bound_for_exact: int = None):
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

        if bound_for_exact is None:
            self._bound_for_exact = self.DEFAULT_BOUND_FOR_EXACT
        else:
            self._bound_for_exact = bound_for_exact

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

        res: List[Set[Element]] = []

        # positions[i][j] = position of element of id i in ranking j, -1 if non-ranked
        positions: ndarray = dataset.get_positions()

        # get the graph of elements and the cost matrix
        gr1, mat_score = ParCons._graph_of_elements(positions, sc)

        # get the strongly connected components in a topological sort
        scc: VertexClustering = gr1.components()
        
        # for each SCC (defining a sub-problem)
        for scc_i in scc:
            set_current_scc: Set[int] = set(scc_i)
            set_current_elements: Set[Element] = {dataset.mapping_id_elem[el_scc] for el_scc in set_current_scc}
            if ParCons._can_be_all_tied(set_current_scc, mat_score):
                res.append(set_current_elements)
            # if there is at least one pair of elements that cannot be tied with minimal cost,
            # then we have no trivial optimal solution. According to the size of the sub-problem, use of
            # the exact algorithm or a heuristics
            else:
                # creation of a new Dataset representing the sub-problem
                sub_problem = dataset.sub_problem_from_elements(set_current_elements)
                if len(scc_i) > self._bound_for_exact:
                    cons_ext = self._auxiliary_alg.compute_consensus_rankings(
                        sub_problem, scoring_scheme, True).consensus_rankings[0]
                    res.extend(cons_ext)
                    optimal = False
                else:
                    cons_ext = ExactAlgorithm(preprocess=False).compute_consensus_rankings(
                        sub_problem, scoring_scheme, True).consensus_rankings[0]
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
    def _can_be_all_tied(id_elements_to_check: Set[int], cost_matrix: ndarray) ->bool:
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

    def get_full_name(self) -> str:
        """

        :return: the name of the Algorithm i.e. "ParCons, uses " + the name of the auxiliary algorithm + " on
        subproblems of size > " + the value of the associated parameter
        """
        return "ParCons, uses  \"" + self._auxiliary_alg.get_full_name() + "\" on subproblems of size >  " + \
            str(self._bound_for_exact)

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True iif the auxiliary algorithm is compatible with the scoring scheme
        :rtype: bool
        """
        return self._auxiliary_alg.is_scoring_scheme_relevant_when_incomplete_rankings(scoring_scheme)
