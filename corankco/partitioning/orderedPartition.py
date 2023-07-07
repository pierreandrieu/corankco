from typing import List, Set, Dict
from corankco.consensus import Consensus
from corankco.element import Element
from corankco.ranking import Ranking


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
        self._mapping_elements_bucketID: Dict[Element, int] = {}
        # map each element with its bucket id
        id_group: int = 0
        for group in partition:
            for elem in group:
                self._mapping_elements_bucketID[elem] = id_group
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
        return len(self._mapping_elements_bucketID)

    @property
    def elements(self) -> Set[Element]:
        """
        Property to get a set of all the elements appearing in a group of the OrderedPartition
        :return: a set of all the elements appearing in a group of the OrderedPartition
        """
        return set(self._mapping_elements_bucketID.keys())

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
        group_e1 = self._mapping_elements_bucketID[element1]
        return group_e1 == self.which_index_is(element2) and group_e1 >= 0

    def which_index_is(self, element: Element) -> int:
        """
        Method to get, given an Element, the int ID of its group
        :param element: The target element
        :return: the index i such that element is in the ith group of the partition. -1 if element is in no group
        """
        if element in self._mapping_elements_bucketID:
            return self._mapping_elements_bucketID[element]
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
