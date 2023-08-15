"""
Module that contains a class as an Exact Algorithm, ILP based, for Kemeny-Young rank aggregation. This algorithm uses
Cplex.
"""

from typing import List, Dict, Set, Tuple, Union
from itertools import combinations
from operator import itemgetter
from numpy import ndarray
from corankco.algorithms.exact.exactalgorithmbase import ExactAlgorithmBase, IncompatibleArgumentsException
from corankco.algorithms.pairwisebasedalgorithm import PairwiseBasedAlgorithm
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.ranking import Ranking
from corankco.element import Element

try:
    import cplex
except ImportError:
    pass


class ExactAlgorithmCplex(ExactAlgorithmBase, PairwiseBasedAlgorithm):
    """

    A class to perform exact optimization on the rank aggregation problem using CPLEX linear programming.
    More information can be found in P.Andrieu, S.Cohen-Boulakia, M.Couceiro, A.Denise, A.Pierrot. A Unifying Rank 
    Aggregation Model to Suitably and Efficiently Aggregate Any Kind of Rankings. 
    https://dx.doi.org/10.2139/ssrn.4353494
    Note: This implementation uses CPLEX, which is proprietary software. Users must download and install CPLEX
    separately
    from the IBM website. While CPLEX is not open source, there is a free version available for academic use.
    More information can be found at: https://www.ibm.com/products/ilog-cplex-optimization-studio

    :ivar _PRECISION_THRESHOLD: float representing the precision threshold used for floating point comparison
    """
    _PRECISION_THRESHOLD = 0.001

    def __init__(self, optimize=True):
        """
        Initializes an instance of the ExactAlgorithmCplex class.

        :param optimize: Boolean for whether to check necessary conditions in order to add constraints. Default is True.
        WARNING: if optimize = True, then, we cannot ensure that all the optimal consensus will be returned
        """
        ExactAlgorithmBase.__init__(self, optimize)

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking=True,
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
        if self._optimize and not return_at_most_one_ranking:
            raise IncompatibleArgumentsException("If attribute optimize = True, then the algorithms "
                                                 "returns a single ranking, hence parameter return_at_most_one_ranking"
                                                 " must be set to false (default value)")

        consensus_rankings: List[Ranking] = self._compute_consensus_rankings_with_optim(
            dataset, scoring_scheme, self._optimize, return_at_most_one_ranking)
        return Consensus(consensus_rankings=consensus_rankings,
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att={ConsensusFeature.NECESSARILY_OPTIMAL: True,
                              ConsensusFeature.ASSOCIATED_ALGORITHM: self.get_full_name()
                              })

    def _compute_consensus_rankings_with_optim(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            look_for_scc: bool,
            return_at_most_one_ranking: bool = True,
    ) -> List[Ranking]:
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The penalty vectors to consider
        :type scoring_scheme: ScoringScheme (class ScoringScheme in package 'distances')
        :param look_for_scc: True to compute Graph pre-processing, True only at the first call, False for each recursive
         call
        :type look_for_scc: bool
        :param return_at_most_one_ranking: the algorithm should not return more than one ranking
        :type return_at_most_one_ranking: bool
        :return one or more optimal rankings if the underlying algorithm can find several equivalent consensus rankings
        If the algorithm is not able to provide multiple consensus, or if return_at_most_one_ranking is True then, it
        should return a list made of the only / the first consensus found.
        In all scenario, the algorithm returns a list of rankings
        :raise ScoringSchemeNotHandledException when the algorithm cannot compute the consensus because the
        implementation of the algorithm does not fit with the scoring scheme
        """

        id_elements: Dict[int, Element] = dataset.mapping_id_elem

        # number of distinct elements in the dataset
        nb_elem: int = dataset.nb_elements

        # 2d matrix where positions[i][j] denotes the position of elem with int id i in ranking j (-1 if non-ranked)
        positions: ndarray = dataset.get_positions()

        # get both the graph of elements defined in GraphBasedAlgorithm interface and the cost matrix
        # which is a 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
        # i after j, i tied with j in the consensus according to the scoring scheme.
        if look_for_scc:
            # computes the graph with the cost matrix
            graph_elements, cost_matrix = ExactAlgorithmCplex.graph_of_elements(positions, scoring_scheme)
            # computes the scc of the graph
            scc = graph_elements.components()
            # to store the consensus ranking
            ranking: List[Set[Element]] = []
            for scc_i in scc:
                # for each scc, if the sub-problem is trivial to solve, then we solve it directly (see ParCons)
                scc_i_set: Set[int] = set(scc_i)
                if ExactAlgorithmCplex.can_be_all_tied(scc_i_set, cost_matrix):
                    ranking.append({id_elements[id_elem] for id_elem in scc_i_set})
                # otherwise, we use the exact algorithm to get a solution to the sub-problem,
                # with this time the boolean set to False to prevent the useless computation of scc
                # (and infinite loop obviously)
                else:
                    # update the ranking to return
                    new_dataset: Dataset = dataset.sub_problem_from_ids(scc_i_set)
                    rankings: List[Ranking] = self._compute_consensus_rankings_with_optim(new_dataset, scoring_scheme,
                                                                                          False, True)
                    for bucket in rankings[0]:
                        ranking.append(bucket)
            return [Ranking(ranking)]

        # else, no more recursive calls to do, single problem to solve
        consensus_rankings: List[Ranking] = []
        cost_matrix = ExactAlgorithmCplex.pairwise_cost_matrix(positions, scoring_scheme)
        # key: int id of cplex variable. Value: Tuple['x' or 't', element1, element2]. x = before, t = tied

        # Cplex object
        my_prob: cplex.Cplex = cplex.Cplex()  # initiate
        my_prob.set_results_stream(None)  # mute

        my_prob.parameters.timelimit.set(3600)  # temps limité à 3600 secondes (1 heure)
        my_prob.parameters.workmem.set(16384)  # mémoire de travail limitée à 2048 Mo (2 Go)
        my_prob.parameters.mip.limits.treememory.set(4096)  # limite de mémoire de l'arbre à 1024 Mo (1 Go

        # Setting the mip-gap parameter. This value represents the relative optimality gap tolerance.
        # The solver stops searching when the relative difference between the best found solution
        # and the best bound is within this value. Setting this value to 0 can lead to incorrect results
        # due to the precision limitations of floating point numbers, hence a small positive value is used.
        my_prob.parameters.mip.tolerances.mipgap.set(0.000001)
        my_prob.parameters.mip.pool.absgap.set(0.000001)

        # out problem is a minimization problem
        my_prob.objective.set_sense(my_prob.objective.sense.minimize)  # we want to minimize the objective function

        # with 4, all the optimal consensus will be found, within a limit of 10000000
        if not return_at_most_one_ranking:
            my_prob.parameters.mip.pool.intensity.set(4)
            my_prob.parameters.mip.limits.populate.set(10000000)

        my_obj: List[float] = []
        my_ub: List[float] = []
        my_lb: List[float] = []
        my_names: List[str] = []

        map_elements_cplex: Dict[int, Tuple[str, int, int]] = \
            ExactAlgorithmCplex._add_cplex_variables(my_obj, my_ub, my_lb, my_names, cost_matrix)

        my_prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types="B"*len(map_elements_cplex), names=my_names)

        # rhs = right hand side
        my_rhs: List[int] = []
        # name of cplex variables
        my_rownames: List[str] = []
        # to store the constraints
        rows: List[List[List[str] | List[float]]] = []

        # inequations : E for Equality, G for >=  and L for <=
        my_sense: str = "E" * int(nb_elem*(nb_elem-1)/2) + "L" * (3*nb_elem * (nb_elem-1) * (nb_elem-2))

        # add binary constraints
        ExactAlgorithmCplex._add_binary_constraints(nb_elem, my_rhs, my_rownames, rows)
        # add transitivity constraints
        ExactAlgorithmCplex._add_transitivity_constraints(nb_elem, my_rhs, my_rownames, rows)
        # add personal constraints
        my_sense += self._add_personal_optimization_constraints(my_rhs, my_rownames, rows, cost_matrix)
        # give the constraints to cplex
        my_prob.linear_constraints.add(lin_expr=rows, senses=my_sense, rhs=my_rhs, names=my_rownames)

        # if return[...] = False, then all the optimal rankings will be stored if optimize = False
        if not return_at_most_one_ranking:
            my_prob.populate_solution_pool()

            nb_optimal_solutions = my_prob.solution.pool.get_num()
            # for each optimal solutions
            for i in range(nb_optimal_solutions):
                # get the variables results
                names = my_prob.solution.pool.get_values(i)
                # construct the consensus
                consensus_rankings.append(ExactAlgorithmCplex._create_consensus(
                    nb_elem, names, map_elements_cplex, id_elements))
        else:
            # get one optimal solution
            my_prob.solve()
            # get the variable results
            cplex_res = my_prob.solution.get_values()
            # compute the consensus
            consensus_rankings.append(ExactAlgorithmCplex._create_consensus(
                nb_elem, cplex_res, map_elements_cplex, id_elements))
        return consensus_rankings

    @staticmethod
    def _add_cplex_variables(my_obj, my_ub: List[float], my_lb: [List[float]], my_names: List[str],
                             mat_score: ndarray) -> Dict[int, Tuple[str, int, int]]:
        """
        Adds the CPLEX variables (before and tied variables) to the given lists.

        :param my_obj: List to which the costs of the variables will be appended
        :param my_ub: List to which the upper bounds of the variables will be appended
        :type my_ub: List[float]
        :param my_lb: List to which the lower bounds of the variables will be appended
        :type my_lb: List[float]
        :param my_names: List to which the names of the variables will be appended
        :type my_names: list[str]
        :param mat_score: 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
                          i after j, i tied with j in the consensus according to the scoring scheme.
        :type mat_score: numpy.ndarray
        :return: A dictionary mapping variable ID to a tuple consisting of variable type (before or tied), element1, and
                 element2
        :rtype: dict[int, tuple[str, int, int]]
        """
        # sets the "before" variables
        map_elements_cplex: Dict[int, Tuple[str, int, int]] = {}
        cpt: int = 0
        nb_elements: int = len(mat_score)
        for i in range(nb_elements):
            for j in range(nb_elements):
                if not i == j:

                    # name of the new cplex variable, x = before whereas t = tied. Here, cost of i before j
                    cplex_var: str = f"x_{i}_{j}"
                    # associated cost in the consensus
                    my_obj.append(mat_score[i][j][0])
                    # the variable is boolean, must be between 0 and 1
                    my_ub.append(1.0)
                    my_lb.append(0.0)
                    my_names.append(cplex_var)
                    # to reconstruct the consensus given final values of variables by cplex
                    map_elements_cplex[cpt] = ("x", i, j)
                    cpt += 1

        # sets the ties variables
        for i in range(nb_elements):
            for j in range(i + 1, nb_elements):
                # t for ties. Variable t_i_j : variable "i tied with j"
                cplex_var: str = f"t_{i}_{j}"
                # associated cost
                my_obj.append(mat_score[i][j][2])
                # boolean variable: 0 or 1 : ub = 1 et lb = 0
                my_ub.append(1.0)
                my_lb.append(0.0)
                my_names.append(cplex_var)
                map_elements_cplex[cpt] = ("t", i, j)
                cpt += 1

        return map_elements_cplex

    @staticmethod
    def _add_binary_constraints(nb_elements: int, my_rhs: List[int], my_rownames: List[str],
                                rows: List[List[Union[List[str], List[float]]]]) -> None:
        """
        Adds the binary constraints to the given lists.

        :param nb_elements: Number of distinct elements in the dataset
        :type nb_elements: int
        :param my_rhs: List to which the right hand side values of the constraints will be appended
        :type my_rhs: list[int]
        :param my_rownames: List to which the names of the constraints will be appended
        :type my_rownames: list[str]
        :param rows: List to which the constraints will be appended
        :type rows: list[list[Union[list[str], list[float]]]]
        """
        # add the binary order constraints
        count: int = len(my_rhs)

        # for each pair of distinct elements
        for i in range(0, nb_elements - 1):
            for j in range(i + 1, nb_elements):
                if not i == j:
                    # unique int id of the new constraint
                    new_constraint_str: str = f"c{count}"
                    my_rownames.append(new_constraint_str)
                    my_rhs.append(1)
                    # i before j var
                    first_var = f"x_{i}_{j}"
                    # j before i var
                    second_var = f"x_{j}_{i}"
                    # i tied with j var
                    third_var = f"t_{i}_{j}"
                    # sum of the 3 binary variables must be one (exactly 1 of the 3 possible relative ordering)
                    row = [[first_var, second_var, third_var], [1.0, 1.0, 1.0]]
                    rows.append(row)
                    count += 1

    @staticmethod
    def _add_transitivity_constraints(nb_elem: int, my_rhs: List[int], my_rownames: List[str],
                                      rows: List[List[Union[List[str], List[float]]]]) -> None:
        """
        Adds the transitivity constraints to the given lists.
        More precisely, for each x, y ,z in the universe:
        x <= y && y < z ==> x < z
        x < y && y <= z ==> x < z
        x == y && y == z ==> x == z

        :param nb_elem: Number of distinct elements in the dataset
        :type nb_elem: int
        :param my_rhs: List to which the right hand side values of the constraints will be appended
        :type my_rhs: list[int]
        :param my_rownames: List to which the names of the constraints will be appended
        :type my_rownames: list[str]
        :param rows: List to which the constraints will be appended
        :type rows: list[list[Union[list[str], list[float]]]]
        """

        # add the transitivity constraints
        count: int = len(my_rhs)
        for i in range(0, nb_elem):
            for j in range(nb_elem):
                if j != i:
                    i_bef_j = f"x_{i}_{j}"
                    if i < j:
                        i_tie_j = f"t_{i}_{j}"
                    else:
                        i_tie_j = f"t_{j}_{i}"
                    for k in range(nb_elem):
                        if k not in (i, j):
                            my_rownames.append(f"c{count}")
                            my_rhs.append(1)
                            count += 1
                            if j < k:
                                j_tie_k = f"t_{j}_{k}"
                            else:
                                j_tie_k = f"t_{k}_{j}"
                            rows.append([[i_bef_j, f"x_{j}_{k}", j_tie_k, f"x_{i}_{k}"], [1., 1., 1., -1.]])

                            my_rownames.append(f"c{count}")
                            my_rhs.append(1)
                            count += 1
                            rows.append([[i_bef_j, i_tie_j, f"x_{j}_{k}", f"x_{i}_{k}"], [1., 1., 1., -1.]])

                            if i < k:
                                i_tie_k = f"t_{i}_{k}"
                            else:
                                i_tie_k = f"t_{k}_{i}"

                            my_rownames.append(f"c{count}")
                            my_rhs.append(3)
                            count += 1
                            rows.append([[i_tie_j, j_tie_k, i_tie_k], [2.0, 2.0, -1.0]])

    def _add_personal_optimization_constraints(self, my_rhs: List[int], my_rownames: List[str],
                                               rows: List[List[Union[List[str], List[float]]]], cost_matrix: ndarray) \
            -> str:
        """
        Adds optimization constraints based on one sufficient condition: see Prop 2 in Andrieu et al., IJAR, 2023.

        :param my_rhs: List of integers representing the right-hand side of the constraints
        :param my_rownames: List of strings representing the names of the constraints
        :param rows: List of lists representing the coefficients of the constraints
        :param cost_matrix: 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
                          i after j, i tied with j in the consensus according to the scoring scheme.
        :return: String representing the type of constraints added, all 'E' for equality constraints
        """

        if not self._optimize:
            return ""

        initial_nb_constraints: int = len(my_rhs)

        # searching for a pair x y of elements such that before(x,y) + before(y,x) > tied(x,y)
        # if no such pair exist, then we can set all tied variables to 0 as we know that at least one optimal consensus
        # is a ranking without ties
        can_have_no_ties: bool = True
        # for e1 in 0 ... nb_elements - 2 and e2 in e1 + 1, nb_elements+1
        for el_1, el_2 in combinations(range(len(cost_matrix)), 2):
            cost_to_tie = cost_matrix[el_1][el_2][2]
            cost_to_place_before = cost_matrix[el_1][el_2][0]
            cost_to_place_after = cost_matrix[el_1][el_2][1]
            calc: float = cost_to_place_before + cost_to_place_after - 2 * cost_to_tie
            # if the test fails, then the optimization cannot be used
            if calc > ExactAlgorithmCplex._PRECISION_THRESHOLD:
                can_have_no_ties = False
                break

        # if the optimization can be done, then all tied variables are set to 0
        if can_have_no_ties:
            for el_1, el_2 in combinations(range(len(cost_matrix)), 2):
                if el_1 > el_2:
                    el_1, el_2 = el_2, el_1

                # set id of constraint, add constraint
                my_rownames.append(f"c{len(my_rhs)}")
                # constraint: 1. * t_elem1_elem2 == 0
                i_tie_j = f"t_{el_1}_{el_2}"
                rows.append([[i_tie_j], [1.]])
                my_rhs.append(0)

        # all the constraints of this function were equality constraints
        return "E" * (len(my_rhs) - initial_nb_constraints)

    @staticmethod
    def _create_consensus(nb_elem: int, cplex_variables: List, map_elements_cplex: Dict, id_elements: Dict) -> Ranking:
        """
        This function creates the consensus ranking from the solved CPLEX problem.

        :param nb_elem: The number of elements to be ranked
        :param cplex_variables: List of CPLEX variables of the problem
        :param map_elements_cplex: Mapping between CPLEX variables and pairs of elements
        :param id_elements: Mapping between unique integer IDs and actual elements
        :return: The consensus ranking as a Ranking object
        """
        count_after: Dict[int, int] = ExactAlgorithmCplex._initialize_defeat_counts(nb_elem)
        ExactAlgorithmCplex._calculate_defeat_counts(cplex_variables, map_elements_cplex, count_after)

        return ExactAlgorithmCplex._create_ranking_from_defeat_counts(count_after, id_elements)

    @staticmethod
    def _initialize_defeat_counts(nb_elem: int) -> Dict[int, int]:
        """
        Initialize the dictionary that will count the defeats of each element.

        :param nb_elem: The number of elements to be ranked
        :return: A dictionary where keys are the unique IDs of elements and values = defeat counts (initialized at 0)
        """
        # at the beginning, 0 defeat for each element
        return {i: 0 for i in range(nb_elem)}

    @staticmethod
    def _create_ranking_from_defeat_counts(count_after: Dict, id_elements: Dict) -> Ranking:
        """
        Create the ranking from the defeat counts of each element.

        :param count_after: Dictionary with the defeat counts of each element
        :param id_elements: Mapping between unique integer IDs and actual elements
        :return: The ranking as a list of sets of elements
        """
        ranking: List[Set[Element]] = []  # Initialize empty ranking

        # Now we create the ranking.
        current_nb_def = 0  # The number of defeats of the current bucket
        bucket: Set[Element] = set()  # Initialize empty bucket
        # Iterate over the elements sorted by defeat count
        for elem, nb_defeats in (sorted(count_after.items(), key=itemgetter(1))):
            if nb_defeats == current_nb_def:  # If the element has the same defeat count as the current bucket
                bucket.add(id_elements.get(elem))  # Add the element to the current bucket
            else:  # If the element has a higher defeat count
                ranking.append(bucket)  # Add the current bucket to the ranking
                bucket = {id_elements.get(elem)}  # Start a new bucket with the current element
                current_nb_def = nb_defeats  # Update the defeat count for the current bucket

        # After iterating over all elements, add the last bucket to the ranking
        ranking.append(bucket)
        return Ranking(ranking)  # Return the ranking

    @staticmethod
    def _calculate_defeat_counts(cplex_variables: List, map_elements_cplex: Dict, count_after: Dict):
        """
        Calculate the number of defeats of each element.

        :param cplex_variables: List of CPLEX variables of the problem
        :param map_elements_cplex: Mapping between CPLEX variables and pairs of elements
        :param count_after: Dictionary that will be updated with the defeat counts
        """
        for i, cplex_variable_i in enumerate(cplex_variables):
            # if the value is set to 1 (value is True)
            if abs(cplex_variable_i - 1) < 0.001:
                # we add +1 to the "loser" element
                var_type, _, loser_elem = map_elements_cplex[i]
                # var_type == x ==> variable is type "i before j" with a value of 1 that is j lose
                if var_type == "x":
                    count_after[loser_elem] += 1

    def get_full_name(self) -> str:
        """
        Return the full name of the algorithm.

        :return: The string 'Exact algorithm ILP Cplex'.
        :rtype: str
        """
        # return "Exact algorithm ILP Cplex"
        if self._optimize:
            return "ExactAlgorithm-optim1-optim2"
        return "ExactAlgorithm"

    def is_scoring_scheme_relevant_when_incomplete_rankings(self, scoring_scheme: ScoringScheme) -> bool:
        """
        Check if the scoring scheme is relevant when the rankings are incomplete.

        :param scoring_scheme: The scoring scheme to be checked.
        :type scoring_scheme: ScoringScheme
        :return: True as ExactAlgorithmCplex can handle any ScoringScheme
        :rtype: bool
        """
        return True
