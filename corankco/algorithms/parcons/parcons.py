"""
Module for ParCons algorithm. More details in ParCons docstring class.
"""

from typing import List, Set
from numpy import ndarray
from corankco.algorithms.rank_aggregation_algorithm import RankAggAlgorithm
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.consensus import Consensus, ConsensusFeature
from corankco.algorithms.bioconsert.bioconsert import BioConsert
from corankco.element import Element
from corankco.ranking import Ranking
from corankco.algorithms.pairwisebasedalgorithm import PairwiseBasedAlgorithm
from corankco.algorithms.exact.exactalgorithmcplexforpaperoptim1 import ExactAlgorithmCplexForPaperOptim1


class ParCons(RankAggAlgorithm, PairwiseBasedAlgorithm):
    """
    ParCons is a graph-based heuristics for Kemeny-Young rank aggregation published in P. Andrieu, B. Brancotte,
    L. Bulteau, S. Cohen-Boulakia, A. Denise, A. Pierrot, S. Vialette, Efficient, robust and effective rank aggregation
    for massive biological datasets. Future Generation Computer Systems, 2021, pp 406–421.
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

    def __init__(self, auxiliary_algorithm: RankAggAlgorithm = None, bound_for_exact: int = None):
        """
        Construct a ParCons instance
        :param auxiliary_algorithm: the rank aggregation algorithm (RankAggAlgorithm instance) to use for
        subproblems whose number of elements is greater than the attribute "bound_for_exact". Default is BioConsert
        :param bound_for_exact: the maximal number of elements for a given sub-problem such that the exact algorithm
        will be used to get a consensus of the sub-problem
        """
        if isinstance(auxiliary_algorithm, RankAggAlgorithm):
            self._auxiliary_alg: RankAggAlgorithm = auxiliary_algorithm
        else:
            self._auxiliary_alg: RankAggAlgorithm = BioConsert(starting_algorithms=None)
        self._bound_for_exact: int = bound_for_exact

        if bound_for_exact is None:
            self._bound_for_exact = self.DEFAULT_BOUND_FOR_EXACT
        else:
            self._bound_for_exact = bound_for_exact

    def compute_consensus_rankings(
            self,
            dataset: Dataset,
            scoring_scheme: ScoringScheme,
            return_at_most_one_ranking: bool = True,
            bench_mode: bool = False
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
        # optimal unless a non-exact auxiliary algorithm is used
        optimal: bool = True

        res: List[Set[Element]] = []
        weak_partition: List[Set[Element]] = []

        # positions[i][j] = position of element of id i in ranking j, -1 if non-ranked
        positions: ndarray = dataset.get_positions()

        # get the graph of elements and the cost matrix
        gr1, mat_score = ParCons.graph_of_elements(positions, scoring_scheme)

        # get the strongly connected components in a topological sort
        scc = gr1.components()
        
        # for each SCC (defining a sub-problem)
        for scc_i in scc:
            set_current_scc: Set[int] = set(scc_i)
            set_current_elements: Set[Element] = {dataset.mapping_id_elem[el_scc] for el_scc in set_current_scc}
            weak_partition.append(set_current_elements)
            if ParCons.can_be_all_tied(set_current_scc, mat_score):
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
                    cons_ext = ExactAlgorithmCplexForPaperOptim1().compute_consensus_rankings(
                        sub_problem, scoring_scheme, True).consensus_rankings[0]
                    res.extend(cons_ext)

        hash_information = {
            ConsensusFeature.ASSOCIATED_ALGORITHM: self.get_full_name(),
            ConsensusFeature.NECESSARILY_OPTIMAL: optimal,
            ConsensusFeature.WEAK_PARTITIONING: weak_partition,
        }
        return Consensus(consensus_rankings=[Ranking(res)],
                         dataset=dataset,
                         scoring_scheme=scoring_scheme,
                         att=hash_information)

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
