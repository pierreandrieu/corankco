"""
Module for an Exact Algorithm, ILP based, using PuLP
"""

from typing import List, Dict, Set
from itertools import combinations
from operator import itemgetter
from numpy import ndarray
import pulp
from igraph import Graph
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.ranking import Ranking
from corankco.element import Element
from corankco.algorithms.pairwisebasedalgorithm import PairwiseBasedAlgorithm


class ExactAlgorithmPulp(RankAggAlgorithm, PairwiseBasedAlgorithm):
    """

    Exact algorithm using free libraries
    """
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
        # mapping unique int id of element -> element
        id_elements: Dict[int, Element] = dataset.mapping_id_elem
        # nb of distinct elements in the dataset
        nb_elem: int = dataset.nb_elements
        # 2d matrix where positions[i][j] = position of element whose int id is i in ranking j, -1 if non-ranked
        positions: ndarray = dataset.get_positions()

        # get the graph of elements and the score matrix
        graph, cost_matrix = ExactAlgorithmPulp.graph_of_elements(positions, scoring_scheme)

        # values of penalty associated to each true pulp variable
        my_values: List[float] = []
        # Pulp variables
        my_vars: List[pulp.LpVariable] = []

        # get the variables of the problem and get a dict to store given the name of a pulp variable its int unique id
        h_vars: Dict[str, int] = ExactAlgorithmPulp._add_pulp_variables(nb_elem, my_values, my_vars, cost_matrix)

        # minimization problem
        prob: pulp.LpProblem = pulp.LpProblem("myProblem", pulp.LpMinimize)

        # add the binary constraints of the problem
        ExactAlgorithmPulp._add_binary_constraints(nb_elem, prob, my_vars, h_vars)
        ExactAlgorithmPulp._add_transitivity_constraints(nb_elem, prob, my_vars, h_vars)
        ExactAlgorithmPulp._add_personal_optimization_constraints(prob, my_vars, h_vars, graph, cost_matrix)
        # objective function
        prob += pulp.lpSum(my_vars[cpt] * my_values[cpt] for cpt in range(len(my_vars)))

        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        h_def: Dict[int, int] = {i: 0 for i in range(nb_elem)}

        for var in my_vars:
            if abs(var.value() - 1) < 0.01 and var.name[0] == "x":
                h_def[int(var.name.split("_")[2])] += 1

        ranking: List[Set[Element]] = []
        current_nb_def: int = 0
        bucket: Set[Element] = set()

        for elem, nb_defeats in (sorted(h_def.items(), key=itemgetter(1))):
            if nb_defeats == current_nb_def:
                bucket.add(id_elements[elem])
            else:
                ranking.append(bucket)
                bucket = {id_elements[elem]}
                current_nb_def = nb_defeats
        ranking.append(bucket)
        return Consensus(consensus_rankings=[Ranking(ranking)],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={ConsensusFeature.NECESSARILY_OPTIMAL: True,
                              ConsensusFeature.ASSOCIATED_ALGORITHM: self.get_full_name(),
                              ConsensusFeature.KEMENY_SCORE: prob.objective.value(),
                              })

    @staticmethod
    def _add_pulp_variables(nb_elem: int, my_values: List[float],
                            my_vars: List[pulp.LpVariable], cost_matrix: ndarray) -> Dict[str, int]:
        """
        Adds the PULP variables (before and tied variables) to the given lists.

        :param nb_elem: The number of distinct elements in the dataset
        :param my_values: List of the float values of penalties associated to each pulp variable
        :type my_values: List[float]
        :param my_vars: List of string variables of the lp problem. x_i_j is the variable for i before j and t_i_j is
        the variable for i tied with j. i and j are integers. x_i_j is not defined if i = j. t_i_j is not defined if
        i >= j
        :type my_vars: List[str]
        :param cost_matrix: 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
                          i after j, i tied with j in the consensus according to the scoring scheme.
        :type cost_matrix: numpy.ndarray
        :return: A dictionary mapping variable name str to its unique int ID
        :rtype: Dict[str, int]
        """
        # sets the "before" variables
        map_variables_int_id: Dict[str, int] = {}

        cpt: int = 0
        for i in range(nb_elem):
            for j in range(nb_elem):
                # for each pair of integers (unique IDs of elements) with i != j, define variable x_i_j as i before j
                if not i == j:
                    name_var = f"x_{i}_{j}"
                    # associate the cost to place i before j in the consensus
                    my_values.append(cost_matrix[i][j][0])
                    # variable is binary
                    my_vars.append(pulp.LpVariable(name_var, 0, 1, cat="Binary"))
                    # associate a unique pulp variable id
                    map_variables_int_id[name_var] = cpt
                    cpt += 1
                    # variable t_i_j = tie i with j in the consensus. Defined only for i < j
                    if i < j:
                        name_var = f"t_{i}_{j}"
                        my_values.append(cost_matrix[i][j][2])
                        my_vars.append(pulp.LpVariable(name_var, 0, 1, cat="Binary"))
                        map_variables_int_id[name_var] = cpt
                        cpt += 1
        return map_variables_int_id

    @staticmethod
    def _add_binary_constraints(nb_elem: int, prob: pulp.LpProblem, my_vars: List[pulp.LpVariable],
                                h_vars: Dict[str, int]) -> None:
        """
        Adds the binary constraints to the given lists.

        :param nb_elem: Number of distinct elements in the dataset
        :type nb_elem: int
        :param prob: the LpProblem
        :type prob: pulp.LpProblem
        :param my_vars: List of string variables of the lp problem. x_i_j is the variable for i before j and t_i_j is
        the variable for i tied with j. i and j are integers. x_i_j is not defined if i = j. t_i_j is not defined if
        i >= j
        :type my_vars: List[str]
        :param h_vars: A dictionary mapping variable name str to its unique int ID
        :type h_vars: Dict[str, int]
        """
        # add the binary order constraints
        for i in range(0, nb_elem - 1):
            for j in range(i + 1, nb_elem):
                if not i == j:
                    # for each (i,j) with i < j, we must have exactly one true variable among
                    # i before j, j before i, i tied with j
                    prob += my_vars[h_vars[f"x_{i}_{j}"]] \
                            + my_vars[h_vars[f"x_{j}_{i}"]] \
                            + my_vars[h_vars[f"t_{i}_{j}"]] == 1

    @staticmethod
    def _add_transitivity_constraints(nb_elem: int, prob: pulp.LpProblem, my_vars: List[pulp.LpVariable],
                                      h_vars: Dict[str, int]) -> None:
        """
        Adds the transitivity constraints to the given lists.
        More precisely, for each x, y ,z in the universe:
        x <= y && y < z ==> x < z
        x < y && y <= z ==> x < z
        x == y && y == z ==> x == z

        :param nb_elem: Number of distinct elements in the dataset
        :type nb_elem: int
        :param prob: the LpProblem
        :type prob: pulp.LpProblem
        :param my_vars: List of string variables of the lp problem. x_i_j is the variable for i before j and t_i_j is
        the variable for i tied with j. i and j are integers. x_i_j is not defined if i = j. t_i_j is not defined if
        i >= j
        :type my_vars: List[str]
        :param h_vars: A dictionary mapping variable name str to its unique int ID
        :type h_vars: Dict[str, int]
        """

        # add the transitivity constraints
        for i in range(0, nb_elem):
            for j in range(nb_elem):
                if j != i:
                    # variable i before j
                    i_bef_j = f"x_{i}_{j}"
                    if i < j:
                        # variable i tied with j, defined only if i < j
                        i_tie_j = f"t_{i}_{j}"
                    else:
                        # variable i tied with j
                        i_tie_j = f"t_{j}_{i}"
                    for k in range(nb_elem):
                        if k not in (i, j):
                            # variable j before k
                            j_bef_k = f"x_{j}_{k}"
                            # variable i before k
                            i_bef_k = f"x_{i}_{k}"
                            if j < k:
                                # variable j tied with k
                                j_tie_k = f"t_{j}_{k}"
                            else:
                                j_tie_k = f"t_{k}_{j}"

                            if i < k:
                                # variable i tied with k
                                i_tie_k = f"t_{i}_{k}"
                            else:
                                i_tie_k = f"t_{k}_{i}"

                            # i < j && j <= k => i < k
                            prob += my_vars[h_vars[i_bef_j]] + my_vars[h_vars[j_bef_k]] \
                                    + my_vars[h_vars[j_tie_k]] - my_vars[h_vars[i_bef_k]] <= 1

                            # i <= j && j < k => i < k
                            prob += my_vars[h_vars[i_bef_j]] + my_vars[h_vars[i_tie_j]] \
                                    + my_vars[h_vars[j_bef_k]] - my_vars[h_vars[i_bef_k]] <= 1

                            # i tied j && j tied k => i tied k
                            prob += 2 * my_vars[h_vars[i_tie_j]] + 2 * my_vars[h_vars[j_tie_k]] \
                                    - my_vars[h_vars[i_tie_k]] <= 3

    @staticmethod
    def _add_personal_optimization_constraints(prob: pulp.LpProblem, my_vars: List[pulp.LpVariable],
                                               h_vars: Dict[str, int], graph_of_elements: Graph, cost_matrix: ndarray):
        """
        Adds optimization constraints based on Prop 2 and Thm 4 in Andrieu et al., IJAR, 2023.
        More precisely, computes the SCC of the graph of elements in a topological sort, and sets that for each x, y
        such that x is in scc[i], y in scc[j] with i < j, we set x before y in consensus.
        Moreover, if for all pairs of elements of a given scc, the cost of tying is high enough vs before / after,
        we set there is no possible ties between elements of this group.

        :param prob: the LpProblem
        :type prob: pulp.LpProblem
        :param my_vars: List of string variables of the lp problem. x_i_j is the variable for i before j and t_i_j is
        the variable for i tied with j. i and j are integers. x_i_j is not defined if i = j. t_i_j is not defined if
        i >= j
        :type my_vars: List[str]
        :param h_vars: A dictionary mapping variable name str to its unique int ID
        :type h_vars: Dict[str, int]
        :param graph_of_elements: The graph of elements presented in Andrieu et al., IJAR, 2023.
        :type graph_of_elements: Graph
        :param cost_matrix: 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
                          i after j, i tied with j in the consensus according to the scoring scheme.
        :type cost_matrix: numpy.ndarray
        """
        # computes the scc of the graph
        cfc = graph_of_elements.components()
        for id_scc, cfc_i in enumerate(cfc):
            # for each scc, check if for all pairs of elements, the below condition is respected
            group_i: Set[int] = set(cfc_i)
            ties_must_be_checked: bool = False
            pairs: combinations = combinations(group_i, 2)
            for el_1, el_2 in pairs:
                cost_e1_before_e2 = cost_matrix[el_1][el_2][0]
                cost_e1_after_e2 = cost_matrix[el_1][el_2][1]
                cost_e1_tied_e2 = cost_matrix[el_1][el_2][2]
                if 2 * cost_e1_tied_e2 < cost_e1_before_e2 + cost_e1_after_e2:
                    ties_must_be_checked = True
                    break
            # if valu of ties[...] is False, then there exists an optimal consensus ranking
            # which has no ties elements within his group
            if not ties_must_be_checked:
                for el_1, el_2 in pairs:
                    if el_1 < el_2:
                        prob += my_vars[h_vars[f"t_{el_1}_{el_2}"]] == 0
                    else:
                        prob += my_vars[h_vars[f"t_{el_2}_{el_1}"]] == 0
            # for all the elements of all the scc after scc[i], they should be placed after
            for j in range(id_scc + 1, len(cfc)):
                for elem_i in group_i:
                    for elem_j in cfc[j]:
                        prob += my_vars[h_vars[f"x_{elem_i}_{elem_j}"]] == 1
                        prob += my_vars[h_vars[f"x_{elem_j}_{elem_i}"]] == 0
                        if elem_i < elem_j:
                            prob += my_vars[h_vars[f"t_{elem_i}_{elem_j}"]] == 0
                        else:
                            prob += my_vars[h_vars[f"x_{elem_j}_{elem_i}"]] == 0

    def get_full_name(self) -> str:
        """
        Return the full name of the algorithm.

        :return: The string 'Exact algotrithm ILP pulp'.
        :rtype: str
        """
        return "Exact algorithm ILP pulp"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True as ExactAlgorithmCplex can handle any ScoringScheme
        :rtype: bool
        """
        return True
