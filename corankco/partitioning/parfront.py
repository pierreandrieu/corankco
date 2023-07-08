from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.element import Element
from typing import Dict, List, Set
from corankco.partitioning.orderedPartition import OrderedPartition
from corankco.algorithms.pairwisebasedalgorithm import PairwiseBasedAlgorithm
from numpy import ndarray, asarray


class ParFront(PairwiseBasedAlgorithm):
    """
    ParFront is an algorithm published in P. Andrieu, B. Brancotte, L. Bulteau, S. Cohen-Boulakia, A. Denise, A. Pierrot
    , S. Vialette, Efficient, robust and effective rank aggregation for massive biological datasets, Future Generation
    Computer Systems, 2021, pp 406–421.
    The objective of this algorithm is the following one: it computes an ordered partition of the elements to rank that
    is a list of sets L = [s1, s2, s3, ..., sk] such that for all i < j, for all x in s[i] and y in s[j], x is before y
    in all the optimal consensus rankings within a Kemeny prism. It is true for any ScoringScheme (see ScoringScheme
    class).
    """

    @staticmethod
    def compute_partition(dataset: Dataset, scoring_scheme: ScoringScheme) -> OrderedPartition:
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The penalty vectors to consider
        :type scoring_scheme: ScoringScheme (class ScoringScheme in package 'distances')
        :return a list of sets of elements such that any exact consensus respects this partitioning
        """
        sc: ndarray = asarray(scoring_scheme.penalty_vectors)
        id_elements: Dict[int, Element] = dataset.mapping_id_elem

        positions: ndarray = dataset.get_positions()
        gr1, mat_score, robust_arcs = ParFront.graph_of_elements(positions, sc)
        sccs = gr1.components()

        # initialization of the partition
        partition: List[Set[int]] = []
        # initially, the partition is a topological sort of the scc of the graph of elements
        for scc in sccs:
            partition.append({x for x in scc})

        # to get the robust partition, we may have to fusion some consecutive groups of the partition
        # more precisely, we have to fusion group i with group i+1 iif there exist x in group[i], y in group[i+1] such
        # that (x,y) is not a robust arc

        # fusion algorithm
        i: int = 0
        while i < len(partition) - 1:
            # group i and group i+1
            set1: Set[int] = partition[i]
            set2: Set[int] = partition[i+1]
            # must they fusion?
            fusion: bool = False
            # for each pairs of elements
            for x in set1:
                for y in set2:
                    # if no robust arc, the fusion must happen
                    if (x, y) not in robust_arcs:
                        fusion = True
                        break
                if fusion:
                    break
            if fusion:
                # fusion: all elements of set2 come into set1 and set2 is removed from the list
                for x in set2:
                    set1.add(x)
                partition.pop(i+1)
                i = max(i-1, 1)
            else:
                i += 1

        # the fusion part is over, now we compute the final ordered partition
        res: List[Set[Element]] = []
        for group in partition:
            g: Set[Element] = set()
            res.append(g)
            for elem in group:
                g.add(id_elements[elem])

        return OrderedPartition(res)
