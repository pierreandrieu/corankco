"""
Module about partitioning. This module is associated to partitioning methods, especially the ones defined in
P. Andrieu, B. Brancotte, L. Bulteau, S. Cohen-Boulakia, A. Denise, A. Pierrot, S. Vialette, Efficient, robust and
effective rank aggregation for massive biological datasets, Future Generation Computer Systems, 2021, pp 406–421.
More precisely, this module defines an ordered partition, and gives two static methods to compute the two ordered
partitions of the above article.
"""

from typing import List, Set, Dict, Iterator
from numpy import ndarray
from corankco.consensus import Consensus
from corankco.element import Element
from corankco.ranking import Ranking
from corankco.dataset import Dataset
from corankco.scoringscheme import ScoringScheme
from corankco.algorithms.pairwisebasedalgorithm import PairwiseBasedAlgorithm


class OrderedPartition:
    """
    Class that implements usefull methods for an ordered partition.
    Note that in Kemeny rank aggregation, elements can be divided in sets of elements to consider independently
    """
    def __init__(self, partition: List[Set[Element]]):
        """
        Initialize the OrderedPartition object
        :param partition: the List of Set of Element that defines the OrderedPartition object
        """
        self._partition: List[Set[Element]] = partition
        self._mapping_elements_bucket_id: Dict[Element, int] = {}
        # map each element with its bucket id
        id_group: int = 0
        for group in partition:
            for elem in group:
                self._mapping_elements_bucket_id[elem] = id_group
            id_group += 1

    @property
    def partition(self) -> List[Set[Element]]:
        """

        :return: The partition, that is the List of List of Element
        """
        return self._partition

    @property
    def nb_elements(self) -> int:
        """

        :return: The number of total elements that is the sum of the number elements of each Set of the OrderedPartition
        """
        return len(self._mapping_elements_bucket_id)

    @property
    def elements(self) -> Set[Element]:
        """
        Property to get a set of all the elements appearing in a group of the OrderedPartition
        :return: a set of all the elements appearing in a group of the OrderedPartition
        """
        return set(self._mapping_elements_bucket_id.keys())

    def get_group_index(self, index: int) -> Set[Element]:
        """
        Get the i-th group of the OrderedPartition, that is the i-th Set of Elements of the partition
        :param index: the index of the part of the partition to get
        :return: the i-th group of the OrderedPartition, that is the i-th Set of Elements of the partition
        """
        return self.partition[index]

    def in_same_group(self, element1: Element, element2: Element) -> bool:
        """
        Return True iif the two elements in parameter are in the same group of the OrderedPartition object
        :param element1:
        :param element2:
        :return: True iif the two elements in parameter are in the same group of the OrderedPartition object
        """
        group_e1 = self._mapping_elements_bucket_id[element1]
        return group_e1 == self.which_index_is(element2) and group_e1 >= 0

    def which_index_is(self, element: Element) -> int:
        """
        Method to get, given an Element, the int ID of its group
        :param element: The target element
        :return: the index i such that element is in the ith group of the partition. -1 if element is in no group
        """
        if element in self._mapping_elements_bucket_id:
            return self._mapping_elements_bucket_id[element]
        return -1

    def consistent_with(self, consensus: Consensus) -> bool:
        """
        Compare the OrderedPartition object with a Consensus object
        :param consensus: the Consensus to compare with
        :return: True iif the Ordered partition and the consensus have the same number of elements, and
        for each i < j, for all x in subgroup i and y in subgroup j of the OrderedPartition, x is
        before y in the consensus. Note that if the Consensus object contains several consensus rankings, only the first
        one is considered
        """

        # res = True unless a pair x, y which does not respect the above property is found
        flag: bool = True
        # take the first consensus ranking of Consensus object
        cons: Ranking = consensus.consensus_rankings[0]
        if consensus.nb_elements != self.nb_elements:
            flag = False

        # initialization of variables
        id_bucket_cons: int = 0
        id_partition: int = 0

        while flag and id_partition < len(self._partition):
            # check the id_partition-th group of the ordered partition
            elements_to_see: Set[Element] = self.get_group_index(id_partition)
            # number of elements in the target group
            nb_elements_to_see: int = len(self.get_group_index(id_partition))

            # check if one element of the consensus is not in the group before all the elements of the group have been
            # seen in the consensus
            while flag and id_bucket_cons < len(cons) and nb_elements_to_see > 0:
                # the current bucket of the consensus to check
                bucket_cons: Set[Element] = cons[id_bucket_cons]
                # if in the target bucket of the consensus, one Element is not in the non-empty target
                # OrderedPartition's group: then the consensus is not consistent with the OrderedPartition
                for element_bucket_cons in bucket_cons:
                    if element_bucket_cons not in elements_to_see:
                        flag = False
                    # if the Element is in the OrderedPartition's target group, then we decrement the number of elements
                    # of the target group to see
                    else:
                        nb_elements_to_see -= 1
                # move to next bucket
                id_bucket_cons += 1
                # move to next target group of the OrderedPartition if all elements have been checked
                if nb_elements_to_see == 0:
                    id_partition += 1
        return flag

    def __str__(self) -> str:
        """
        returns a string representation of the object:
        the str of the List of set of elements
        :return: The str representing the list of set of elements
        """
        return str(self._partition)

    def __repr__(self) -> str:
        """
        returns a string representation of the object:
        the str of the List of set of elements
        :return: The str representing the list of set of elements
        """
        return str(self)

    def __iter__(self) -> Iterator[Set[Element]]:
        """
        Returns an iterator over the groups of elements in the OrderedPartition object.
        This allows the OrderedPartition to be iterated over using a for loop,
        yielding each part of the partition in turn.

        return: An iterator over the groups of elements in the OrderedPartition.

        """
        return iter(self._partition)

    @staticmethod
    def parfront_partition(dataset: Dataset, scoring_scheme: ScoringScheme) -> 'OrderedPartition':
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The penalty vectors to consider
        :type scoring_scheme: ScoringScheme (class ScoringScheme in package 'distances')
        :return a list of sets of elements such that any exact consensus respects this partitioning
        """
        id_elements: Dict[int, Element] = dataset.mapping_id_elem

        positions: ndarray = dataset.get_positions()
        gr1, _, robust_arcs = \
            PairwiseBasedAlgorithm.graph_of_elements_with_robust_arcs(positions, scoring_scheme)
        sccs = gr1.components()

        # initialization of the partition
        # initially, the partition is a topological sort of the scc of the graph of elements
        partition: List[Set[int]] = [set(scc) for scc in sccs]

        # to get the robust partition, we may have to fusion some consecutive groups of the partition
        # more precisely, we have to fusion group i with group i+1 iif there exist x in group[i], y in group[i+1] such
        # that (x,y) is not a robust arc

        # fusion algorithm
        index: int = 0
        while index < len(partition) - 1:
            # group i and group i+1
            set1: Set[int] = partition[index]
            set2: Set[int] = partition[index + 1]
            # must they fusion?
            fusion: bool = False
            # for each pairs of elements
            for el_1 in set1:
                for el_2 in set2:
                    # if no robust arc, the fusion must happen
                    if (el_1, el_2) not in robust_arcs:
                        fusion = True
                        break
                if fusion:
                    break
            if fusion:
                # fusion: all elements of set2 come into set1 and set2 is removed from the list
                for el_1 in set2:
                    set1.add(el_1)
                partition.pop(index + 1)
                index = max(index - 1, 1)
            else:
                index += 1

        # the fusion part is over, now we compute the final ordered partition
        return OrderedPartition([set(id_elements[elem] for elem in group) for group in partition])

    @staticmethod
    def parcons_partition(dataset: Dataset, scoring_scheme: ScoringScheme) -> 'OrderedPartition':
        """
        :param dataset: A dataset containing the rankings to aggregate
        :type dataset: Dataset (class Dataset in package 'datasets')
        :param scoring_scheme: The ScoringScheme to consider (see ScoringScheme class)
        :type scoring_scheme: ScoringScheme
        :return a list of sets of elements such that there exists an exact consensus ranking which is consistent with
        the obtained partitioning
        """
        # mapping between the unique ID of elements and the related element
        id_elements: Dict[int, Element] = dataset.mapping_id_elem
        # 2D matrix ndarray, position[i][j] = position of element whose unique ID is i in ranking j, -1 if non-ranked
        positions: ndarray = dataset.get_positions()
        # computes the graph of element presented in the article of the docstring class
        gr1, _ = PairwiseBasedAlgorithm.graph_of_elements(positions, scoring_scheme)
        # the partition is a topological sort of the scc of the graph of elements
        sccs = gr1.components()

        # initialization of the partition
        partition: List[Set[Element]] = []
        # for each scc, add the elements of the scc within a set
        for scc in sccs:
            partition.append({id_elements[x] for x in scc})

        return OrderedPartition(partition)
