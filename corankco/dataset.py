from typing import List, Dict, Set
import numpy as np
from corankco.utils import get_rankings_from_file, get_rankings_from_folder, write_rankings, \
    dump_ranking_with_ties_to_str, name_file
from corankco.rankingsgeneration.rankingsgenerate import create_rankings, uniform_permutation


class EmptyDatasetException(Exception):
    pass


class Dataset:
    def __init__(self, rankings: str or List[List[List or Set[int or str]]]):
        self.__nb_rankings = -1
        self.__nb_elements = -1
        self.__is_complete = None
        self.__with_ties = None
        if type(rankings) == str:
            rankings_list = dump_ranking_with_ties_to_str(rankings)
        else:
            rankings_list = rankings
        self.__name = "manual"
        if len(rankings_list) == 0:
            raise EmptyDatasetException

        # check if all elements are integers. If yes, all str are converted to integers
        all_integers = True
        id_ranking = 0
        while id_ranking < len(rankings_list) and all_integers:
            ranking_i = rankings_list[id_ranking]
            id_bucket = 0
            if len(ranking_i) > 0:
                while id_bucket < len(ranking_i) and all_integers:
                    bucket_i = ranking_i[id_bucket]
                    for element in bucket_i:
                        if not isinstance(element, int) and not element.isdigit():
                            all_integers = False
                            break
                    id_bucket += 1
            id_ranking += 1

        if not all_integers:
            rankings_final = rankings_list

        else:
            rankings_final = []
            id_ranking = 0
            while id_ranking < len(rankings_list) and all_integers:
                ranking_i = rankings_list[id_ranking]
                ranking_int = []
                id_bucket = 0
                while id_bucket < len(ranking_i) and all_integers:
                    bucket_i = ranking_i[id_bucket]
                    if isinstance(bucket_i, set):
                        bucket_int = set(map(int, bucket_i))
                    else:
                        bucket_int = list(map(int, bucket_i))
                    ranking_int.append(bucket_int)
                    id_bucket += 1
                rankings_final.append(ranking_int)
                id_ranking += 1

        # updates previous values with right values for n, m and complete
        self.__set_rankings_and_update_properties(rankings=rankings_final)
        if self.n == 0:
            raise EmptyDatasetException("Datast must not be empty")

    @staticmethod
    def get_ranking_from_file(path: str):
        d = Dataset(get_rankings_from_file(path))
        d.name = name_file(path)
        return d

    def __get_rankings(self) -> List[List[List or Set[int or str]]]:
        return self.__rankings

    def __get_nb_elements(self) -> int:
        return self.__nb_elements

    def __get_path(self) -> str:
        return self.__name

    def __get_nb_rankings(self) -> int:
        return self.__nb_rankings

    def __get_is_complete(self) -> bool:
        return self.__is_complete

    def __get_with_ties(self) -> bool:
        return self.__with_ties

    def __set_nb_elements(self, n: int):
        self.__nb_elements = n

    def __set_nb_rankings(self, m: int):
        self.__nb_rankings = m

    def __set_is_complete(self, complete: bool):
        self.__is_complete = complete

    def __set_with_ties(self, with_ties: bool):
        self.__with_ties = with_ties

    def __set_path(self, path: str):
        self.__name = path

    def __set_rankings_and_update_properties(self, rankings: List[List[List or Set[int or str]]]):
        self.__rankings = rankings
        self.__nb_rankings = len(rankings)
        self.__is_complete = self.__check_if_rankings_complete_and_update_n()

    # number of elements
    n = property(__get_nb_elements, __set_nb_elements)
    # number of rankings
    m = property(__get_nb_rankings, __set_nb_rankings)
    # input rankings
    rankings = property(__get_rankings, __set_rankings_and_update_properties)
    # boolean: True iif all the rankings are on the same set of elements
    is_complete = property(__get_is_complete, __set_is_complete)
    # boolean: True iif there exists at least a bucket of size >= 2
    with_ties = property(__get_with_ties, __set_with_ties)
    # name of the dataset
    name = property(__get_path, __set_path)

    def __str__(self) -> str:
        return str(self.rankings)

    def description(self) -> str:
        return "Dataset description:\n\telements:"+str(self.n)+"\n\trankings:"+str(self.m)+"\n\tcomplete:"\
               + str(self.is_complete) + "\n\twith ties: "+str(self.with_ties) + "\n\t"+"rankings:\n"\
               + "\n".join("\t\tr"+str(i+1)+" = "+str(self.rankings[i]) for i in range(len(self.rankings)))

    # to update properties
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

    # map each element with {1, ..., n} (bijection)
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

    # returns a numpy ndarray where positions[i][j] is the position of element i in ranking j. Missing: element: -1
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

    # returns the pairwise cost matrix
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

    def write(self, path):
        write_rankings(self.rankings, path)

    @staticmethod
    def get_uniform_dataset(nb_elem: int, nb_rankings: int):
        return Dataset(uniform_permutation(nb_elem, nb_rankings))

    @staticmethod
    def get_random_dataset_markov(nb_elem: int, nb_rankings: int, step, complete: bool = False):
        return Dataset(create_rankings(nb_elem, nb_rankings, step, complete))

    @staticmethod
    def get_datasets_from_folder(path_folder: str) -> List:
        datasets = []
        datasets_rankings = get_rankings_from_folder(path_folder)
        for dataset_ranking, file_path in datasets_rankings:
            dataset = Dataset(dataset_ranking)
            dataset.name = file_path
            datasets.append(dataset)
        return datasets

    @staticmethod
    def get_dataset_from_file(path_file: str):
        return Dataset(path_file)

    def __lt__(self, other):
        return self.n < other.n or (self.n == other.n and self.m < other.m)

    def __le__(self, other):
        return self.n <= other.n or (self.n == other.n and self.m <= other.m)

    def __eq__(self, other):
        return self.n == other.n and self.m == other.m

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.n > other.n or (self.n == other.n and self.m > other.m)

    def __ge__(self, other):
        return self.n >= other.n or (self.n == other.n and self.m >= other.m)

    def __repr__(self):
        return str(self.rankings)


    def contains_element(self, element: str or int) -> bool:
        to_check = str(element)
        for ranking in self.rankings:
            for bucket in ranking:
                for elem in bucket:
                    if str(elem) == to_check:
                        return True
        return False


class DatasetSelector:
    def __init__(self,
                 nb_elem_min: int = 0,
                 nb_elem_max: float = float('inf'),
                 nb_rankings_min: int = 0,
                 nb_rankings_max: float = float('inf')):
        self.__nb_elem_min = nb_elem_min
        self.__nb_elem_max = nb_elem_max
        self.__nb_rankings_min = nb_rankings_min
        self.__nb_rankings_max = nb_rankings_max

    def __get_nb_elem_min(self) -> int:
        return self.__nb_elem_min

    def __get_nb_rankings_min(self) -> int:
        return self.__nb_rankings_min

    def __get_nb_elem_max(self) -> int or float:
        return self.__nb_elem_max

    def __get_nb_rankings_max(self) -> int or float:
        return self.__nb_rankings_max

    nb_elem_max = property(__get_nb_elem_max)
    nb_elem_min = property(__get_nb_elem_min)
    nb_rankings_max = property(__get_nb_rankings_max)
    nb_rankings_min = property(__get_nb_rankings_min)

    def select_datasets(self, list_datasets: List) -> List:
        res = []
        for dataset in list_datasets:
            if self.__nb_elem_min <= dataset.n <= self.__nb_elem_max:
                if self.__nb_rankings_min <= dataset.m <= self.__nb_rankings_max:
                    res.append(dataset)
        return res

    def __str__(self) -> str:
        return "nb elements between " + str(self.__nb_elem_min) + " and " + str(self.__nb_elem_max) + \
               "; nb rankings between " + str(self.__nb_rankings_min) + " and " + str(self.__nb_rankings_max)

    def __repr__(self) -> str:
        return self.__str__()
