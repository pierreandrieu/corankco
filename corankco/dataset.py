from typing import List, Dict, Set
import numpy as np


class EmptyDatasetException(Exception):
    pass


class Dataset:
    def __init__(self,  r: List[List[List or Set[int or str]]]):
        self.__set_nb_rankings(-1)
        self.__set_nb_elements(-1)
        self.__set_is_complete(None)
        self.__set_with_ties(None)
        if len(r) == 0:
            raise EmptyDatasetException
        # updates previous values with right values for n, m and complete
        self.__set_rankings_and_update_properties(r)

    def __get_rankings(self) -> List[List[List or Set[int or str]]]:
        return self.__rankings

    def __get_nb_elements(self) -> int:
        return self.__nb_elements

    def __get_nb_rankings(self) -> int:
        return self.__nb_rankings

    def __get_is_complete(self) -> bool:
        return self.__is_complete

    def __get_with_ties(self) -> bool:
        return self.__with_ties

    def __set_rankings_and_update_properties(self, rankings: List[List[List or Set[int or str]]]):
        self.__rankings = rankings
        self.__set_nb_rankings(len(rankings))
        self.__set_is_complete(self.__check_if_rankings_complete_and_update_n())

    def __set_nb_elements(self, n: int):
        self.__nb_elements = n

    def __set_nb_rankings(self, m: int):
        self.__nb_rankings = m

    def __set_is_complete(self, complete: bool):
        self.__is_complete = complete

    def __set_with_ties(self, with_ties: bool):
        self.__with_ties = with_ties

    n = property(__get_nb_elements, __set_nb_elements)
    m = property(__get_nb_rankings, __set_nb_rankings)
    rankings = property(__get_rankings, __set_rankings_and_update_properties)
    is_complete = property(__get_is_complete, __set_is_complete)
    with_ties = property(__get_with_ties, __set_with_ties)

    def __str__(self)->str:
        print("ok")
        return str(self.rankings)

    def description(self)->str:
        return "Dataset description:\n\telements:"+str(self.n)+"\n\trankings:"+str(self.m)+"\n\tcomplete:"\
               + str(self.is_complete) + "\n\twith ties: "+str(self.with_ties) + "\n\t"+"rankings:\n"\
               + "\n".join("\t\tr"+str(i+1)+" = "+str(self.rankings[i]) for i in range(len(self.rankings)))

    def __check_if_rankings_complete_and_update_n(self):
        self.with_ties = False
        if len(self.rankings) == 0:
            self.n = 0
            self.m = 0
        else:
            elements = {}

            for ranking in self.rankings:
                nb_elements = 0
                for bucket in ranking:
                    nb_elements += len(bucket)
                    if len(bucket) > 1:
                        self.with_ties = True
                    for element in bucket:
                        if element not in elements:
                            elements[element] = 1
                        else:
                            elements[element] += 1
            self.n = len(elements)
            self.m = len(self.rankings)
            for key in elements.keys():
                if elements[key] != self.m:
                    return False
        return True

    def map_elements_id(self) -> Dict[int or str, int]:
        h = {}
        id_elem = 0
        for ranking in self.rankings:
            for bucket in ranking:
                for elem in bucket:
                    if elem not in h:
                        h[elem] = id_elem
                        id_elem += 1
        return h

    def get_positions(self, elements_id: Dict[str or int, int]) -> np.ndarray:
        n = self.n
        m = self.m
        positions = np.zeros((n, m)) - 1
        id_ranking = 0
        for ranking in self.rankings:
            id_bucket = 0
            for bucket in ranking:
                for elem in bucket:
                    positions[elements_id.get(elem)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def pairs_relative_positions(self, positions: np.ndarray) -> np.ndarray:
        n = self.n
        m = self.m
        matrix = np.zeros((n * n, 6))
        for e1 in range(n-1, -1, -1):
            ind1 = n * e1 + e1
            ind2 = ind1
            for e2 in range(e1-1, -1, -1):
                ind1 -= 1
                ind2 -= n
                a = np.count_nonzero(positions[e1] + positions[e2] == -2)
                b = np.count_nonzero(positions[e1] == positions[e2])
                c = np.count_nonzero(positions[e2] == -1)
                d = np.count_nonzero(positions[e1] == -1)
                e = np.count_nonzero(positions[e1] < positions[e2])
                matrix[ind1] = [e-d+a, b-a, m-(a+b+c+d+e), c-a, d-a, a]
                matrix[ind2] = [e - d + a, b - a, m - (a + b + c + d + e), c - a, d - a, a]

        return matrix

    def unified_rankings(self):
        copy_rankings = []
        elements = set()
        for ranking in self.rankings:
            new_ranking = []
            copy_rankings.append(new_ranking)
            for bucket in ranking:
                new_ranking.append(list(bucket))
                for element in bucket:
                    elements.add(element)

        for ranking in copy_rankings:
            elem_ranking = set(elements)
            for bucket in ranking:
                for element in bucket:
                    elem_ranking.remove(element)
            if len(elem_ranking) > 0:
                ranking.append(list(elem_ranking))
        return copy_rankings

    def unified_dataset(self):
        return Dataset(self.unified_rankings())
