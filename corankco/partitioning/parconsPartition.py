from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.element import Element
from typing import Dict, List, Set
from corankco.partitioning.orderedPartition import OrderedPartition
from corankco.algorithms.pairwisebasedalgorithm import PairwiseBasedAlgorithm
from numpy import ndarray, asarray


class ParConsPartition(PairwiseBasedAlgorithm):
    """
    ParConsPartition is a preprocessing algorithm published in
    https://www.researchgate.net/publication/352277711_Efficient_robust_and_effective_rank_aggregation_for_massive_biological_datasets
    The objective of this algorithm is the following one: it computes an ordered partition of the elements to rank that
    is a list of sets L = [s1, s2, s3, ..., sk] such that there exists an optimal consensus ranking, in the sens of
    Kemeny, which is consistent with this partitioning.
    """

    @staticmethod
    def compute_partition(dataset: Dataset, scoring_scheme: ScoringScheme) -> OrderedPartition:
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The ScoringScheme to consider (see ScoringScheme class)
        :type scoring_scheme: ScoringScheme
        :return a list of sets of elements such that there exists an exact consensus ranking which is consistent with
        the obtained partitioning
        """
        sc: ndarray = asarray(scoring_scheme.penalty_vectors)
        # mapping between the unique ID of elements and the related element
        id_elements: Dict[int, Element] = dataset.mapping_id_elem
        # 2D matrix ndarray, position[i][j] = position of element whose unique ID is i in ranking j, -1 if non-ranked
        positions: ndarray = dataset.get_positions()
        # computes the graph of element presented in the article of the docstring class
        gr1, mat_score, robust_arcs = ParConsPartition.graph_of_elements(positions, sc)
        # the partition is a topological sort of the scc of the graph of elements
        sccs = gr1.components()

        # initialization of the partition
        partition: List[Set[Element]] = []
        # for each scc, add the elements of the scc within a set
        for scc in sccs:
            partition.append({id_elements[x] for x in scc})

        return OrderedPartition(partition)

    @staticmethod
    def size_of_biggest_subproblem(dataset: Dataset, scoring_scheme: ScoringScheme) -> int:
        """
        Return the size of the biggest strongly connected component of the graph of elements defined in the article
        presented in the DocString class
        :param dataset: the dataset (list of rankings) to consider
        :param scoring_scheme: the scoring scheme to consider
        :return:
        """
        return max(map(len, ParConsPartition.compute_partition(dataset, scoring_scheme).partition))
