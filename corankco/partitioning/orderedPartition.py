from typing import List, Set
from corankco.consensus import Consensus


class OrderedPartition:
    def __init__(self, partition: List[Set[int or str]]):
        self.__partition = partition
        self.__hash_elements_with_index_groups = {}
        id_group = 0
        for group in partition:
            for elem in group:
                self.__hash_elements_with_index_groups[elem] = id_group
            id_group += 1

    def __get_partition(self) -> List[Set[int or str]]:
        return self.__partition

    def __get_nb_elements(self) -> int:
        return len(self.__hash_elements_with_index_groups)

    def __get_elements(self) -> Set:
        return set(self.__hash_elements_with_index_groups.keys())

    def get_group(self, index: int) -> Set[int or str]:
        return self.partition[index]

    def in_same_group(self, element1: int or str, element2: int or str) -> bool:
        group_e1 = self.__hash_elements_with_index_groups[element1]
        return group_e1 == self.which_index_is(element2) and group_e1 >= 0

    def which_index_is(self, element: int or str) -> int:
        if element in self.__hash_elements_with_index_groups:
            return self.__hash_elements_with_index_groups[element]
        return -1

    def consistent_with(self, consensus: Consensus) -> bool:
        flag = True
        cons = consensus.consensus_rankings[0]
        if consensus.nb_elements != self.nb_elements:
            flag = False
        id_bucket_cons = 0
        id_partition = 0
        while flag and id_partition < len(self.__partition):
            elements_to_see = self.get_group(id_partition)
            nb_elements_to_see = len(self.get_group(id_partition))
            while flag and id_bucket_cons < len(cons) and nb_elements_to_see > 0:
                bucket_cons = cons[id_bucket_cons]
                for element_bucket_cons in bucket_cons:
                    if element_bucket_cons not in elements_to_see:
                        flag = False
                    else:
                        nb_elements_to_see -= 1
                id_bucket_cons += 1
                if nb_elements_to_see == 0:
                    id_partition += 1
        return flag

    def __str__(self) -> str:
        return str(self.__partition)

    def __repr__(self) -> str:
        return str(self)

    partition = property(__get_partition)
    elements = property(__get_elements)
    nb_elements = property(__get_nb_elements)
