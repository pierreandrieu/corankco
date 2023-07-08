from typing import List, Union
from itertools import combinations
from .exactalgorithmcplex import ExactAlgorithmCplex
from numpy import ndarray


class ExactAlgorithmCplexForPaperOptim1(ExactAlgorithmCplex):
    """
    A class to perform exact optimization on the rank aggregation problem using CPLEX linear programming.
    This class was used for the experiments presented in Andrieu et al., IJAR, 2023. The objective is to
    consider only one of the possible optimizations: a sufficient condition to ensure that at least one
    optimal consensus is a ranking without ties
    This class only re-defines the function to get personalized contraints based on sufficient conditions.

    More information can be found in the following article: Andrieu et al., IJAR, 2023.
    """
    def __init__(self):
        super().__init__(optimize=False)

    def _add_personal_optimization_constraints(self, my_rhs: List[int], my_rownames: List[str],
                                               rows: List[List[Union[List[str], List[float]]]],
                                               cost_matrix: ndarray) -> str:
        """
        Adds optimization constraints based on one sufficient condition: see Prop 2 in Andrieu et al., IJAR, 2023.

        :param my_rhs: List of integers representing the right-hand side of the constraints
        :param my_rownames: List of strings representing the names of the constraints
        :param rows: List of lists representing the coefficients of the constraints
        :param cost_matrix: 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
                          i after j, i tied with j in the consensus according to the scoring scheme.
        :return: String representing the type of constraints added, all 'E' for equality constraints
        """
        initial_nb_constraints: int = len(my_rhs)
        count: int = len(my_rhs)

        # searching for a pair x y of elements such that before(x,y) + before(y,x) > tied(x,y)
        # if no such pair exist, then we can set all tied variables to 0 as we know that at least one optimal consensus
        # is a ranking without ties
        can_have_no_ties: bool = True
        # for e1 in 0 ... nb_elements - 2 and e2 in e1 + 1, nb_elements+1
        for e1, e2 in combinations(range(len(cost_matrix)), 2):
            cost_to_tie = cost_matrix[e1][e2][2]
            cost_to_place_before = cost_matrix[e1][e2][0]
            cost_to_place_after = cost_matrix[e1][e2][1]
            calc: float = cost_to_place_before + cost_to_place_after - 2 * cost_to_tie
            # if the test fails, then the optimization cannot be used
            if calc > ExactAlgorithmCplex._PRECISION_THRESHOLD:
                can_have_no_ties = False
                break

        # if the optimization can be done, then all tied variables are set to 0
        if can_have_no_ties:
            for e1, e2 in combinations(range(len(cost_matrix)), 2):
                if e1 > e2:
                    tmp = e1
                    e1 = e2
                    e2 = tmp
                # set id of constraint, add constraint
                my_rownames.append("c%s" % count)
                # constraint: 1. * t_elem1_elem2 == 0
                i_tie_j = "t_%s_%s" % (e1, e2)
                rows.append([[i_tie_j], [1.]])
                my_rhs.append(0)
                count += 1

        # all the constraints of this function were equality constraints
        return "E" * (len(my_rhs) - initial_nb_constraints)

    def get_full_name(self) -> str:        # return "Exact algorithm ILP Cplex"

        """
        Return the full name of the algorithm.

        :return: The string 'Exact algorithm ILP Cplex'.
        :rtype: str
        """
        return "ExactAlgorithm-optim1"
