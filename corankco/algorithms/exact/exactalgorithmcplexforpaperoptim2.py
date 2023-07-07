from typing import List, Union, Set
from itertools import combinations
from algorithms.exact.exactalgorithmcplex import ExactAlgorithmCplex
from numpy import ndarray


class ExactAlgorithmCplexForPaperOptim2(ExactAlgorithmCplex):
    """
    A class to perform exact optimization on the rank aggregation problem using CPLEX linear programming.
    This class was used for the experiments presented in Andrieu et al., IJAR, 2023. The objective is to
    consider only one of the possible optimizations: the decomposition in scc of the graph of elements

    This class only re-defines the function to get personalized contraints based on sufficient conditions.

    More information can be found in the following article: Andrieu et al., IJAR, 2023.
    """
    def _add_personal_optimization_constraints(self, my_rhs: List[int], my_rownames: List[str],
                                               rows: List[List[Union[List[str], List[float]]]], graph_elements,
                                               cost_matrix: ndarray) -> str:
        """
        Adds optimization constraints based on one sufficient condition: see Theorem 4 in Andrieu et al., IJAR, 2023.

        :param my_rhs: List of integers representing the right-hand side of the constraints
        :param my_rownames: List of strings representing the names of the constraints
        :param rows: List of lists representing the coefficients of the constraints
        :param graph_elements: The graph of elements defined in Andrieu et al., IJAR, 2023.
        :param cost_matrix: 3D matrix where matrix[i][j][0], then [1], then [2] denote the cost to have i before j,
                          i after j, i tied with j in the consensus according to the scoring scheme.
        :return: String representing the type of constraints added, all 'E' for equality constraints
        """
        initial_nb_constraints: int = len(my_rhs)
        count: int = len(my_rhs)

        # gets the scc of the graph in a topological sort
        scc = graph_elements.components()
        scc_sets: List[Set[int]] = []
        for scc_i in scc:
            scc_sets.append({x for x in scc_i})

        for i in range(len(scc) - 1):
            # first step : manage constraints within the ith scc. Checks :
            # * if all the elements of the scc can be tied with minimal cost. If yes, then they will be tied
            # * if, for each x != y in the scc, we have mat_score[i][j][0] + mat_score[i][j][1] - 2 * mat_score[i][j][2]
            # then, we an ensure that there exists one optimal consensus for this sub-problem with no ties.

            can_be_all_tied: bool = True

            # tests all the ordered pairs of elements in ith scc.
            for e1, e2 in combinations(scc_sets[i], 2):
                cost_to_tie = cost_matrix[e1][e2][2]
                cost_to_place_before = cost_matrix[e1][e2][0]
                cost_to_place_after = cost_matrix[e1][e2][1]
                # if for a given pair, the cost of tying is not minimal, the associated boolean is set to False
                if can_be_all_tied:
                    if -0.001 <= cost_to_tie - min(cost_to_place_before, cost_to_place_after) <= 0.001:
                        can_be_all_tied = False
                        break

            # if elements of the scc can be all tied with minimal cost:
            if can_be_all_tied:
                for elem1, elem2 in combinations(scc_sets[i], 2):
                    # for each pair of elements (with elem1 < elem2)

                    # set id of constraint, add constraint
                    my_rownames.append("c%s" % count)
                    # constraint: 1. * t_elem1_elem2 == 1
                    i_tie_j = "t_%s_%s" % (elem1, elem2)
                    rows.append([[i_tie_j], [1.]])
                    my_rhs.append(1)
                    count += 1

            # now, add the before relations of the graph between i_th scc and all the j_th scc, j > i
            for j in range(i + 1, len(scc)):
                # get in a set the elements of scc_j

                # for each element e1 of the 1st scc, element e2 of the 2nd scc, e1 can be set before e2
                for elem1 in scc_sets[i]:
                    for elem2 in scc_sets[j]:
                        # set id of constraint, add constraint
                        my_rownames.append("c%s" % count)
                        # constraint: 1. * x_elem1_elem2 == 1
                        i_bef_j = "x_%s_%s" % (elem1, elem2)
                        rows.append([[i_bef_j], [1.]])
                        my_rhs.append(1)
                        count += 1

        # all the constraints of this function were equality constraints
        return "E" * (len(my_rhs) - initial_nb_constraints)