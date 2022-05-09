from typing import List, Dict, Set, Tuple
import numpy as np
from corankco.utils import get_rankings_from_file, get_rankings_from_folder, write_rankings, \
    dump_ranking_with_ties_to_str, name_file
from corankco.rankingsgeneration.rankingsgenerate import create_rankings, uniform_permutation


class EmptyDatasetException(Exception):
    pass


class Dataset:
    def __init__(self, rankings: str or List[List[List or Set[int or str]]]):
        self.__mapping_elements_id = {}
        self.__rankings, self.__is_complete, self.__with_ties = self.__analyse_rankings(rankings)
        self.__name = ""

    def __analyse_rankings(self,
                           rankings: List[List[List or Set[int or str]]]) \
            -> Tuple[List[List[List or Set[int or str]]], bool, bool]:

        if type(rankings) == str:
            rankings_list = dump_ranking_with_ties_to_str(rankings)
        else:
            rankings_list = rankings
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
            rankings_final = []
            for ranking_l in rankings_list:
                ranking_final = []
                for bucket_l in ranking_l:
                    bucket_final = set()
                    bucket_final.update(bucket_l)
                    ranking_final.append(bucket_final)
                rankings_final.append(ranking_final)

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

        # check if rankings are complete or not, and with or without ties

        with_ties = False
        complete = True
        elements_appearance = {}
        for ranking in rankings_final:
            nb_elements = 0
            for bucket in ranking:
                nb_elements += len(bucket)
                if len(bucket) > 1:
                    with_ties = True
                for element in bucket:
                    if element not in elements_appearance:
                        elements_appearance[element] = 1
                    else:
                        elements_appearance[element] += 1

        if len(elements_appearance) == 0:
            raise EmptyDatasetException("Dataset must not be empty")

        id_element = 0
        for key in elements_appearance.keys():
            self.__mapping_elements_id[key] = id_element
            id_element += 1
            if elements_appearance[key] != len(rankings_final):
                complete = False
        return rankings_final, complete, with_ties

    def remove_empty_rankings(self):
        rankings_new = []
        for ranking in self.rankings:
            if len(ranking) > 0:
                rankings_new.append(ranking)
        self.__rankings, self.__is_complete, self.__with_ties = self.__analyse_rankings(rankings_new)

    def remove_elements_rate_presence_lower_than(self, rate_presence: float):
        presence = {}
        for element in self.elements:
            presence[element] = 0
        for ranking in self.__rankings:
            for bucket in ranking:
                for element in bucket:
                    presence[element] += 1
        elements_to_remove = set()
        for element, nb_rankings_present in presence.items():
            if nb_rankings_present / self.nb_rankings < rate_presence:
                elements_to_remove.add(element)
        self.remove_elements(elements_to_remove)

    def remove_elements(self, elements_to_remove: Set):
        new_rankings = []
        for old_ranking in self.rankings:
            new_ranking = []
            for old_bucket in old_ranking:
                new_bucket = []
                for old_element in old_bucket:
                    if old_element not in elements_to_remove:
                        new_bucket.append(old_element)
                if len(new_bucket) > 0:
                    new_ranking.append(new_bucket)
            if len(new_ranking) > 0:
                new_rankings.append(new_ranking)
        for element_to_remove in elements_to_remove:
            self.__mapping_elements_id.pop(element_to_remove)
        self.__rankings, self.__is_complete, self.__with_ties = self.__analyse_rankings(new_rankings)

    @staticmethod
    def get_ranking_from_file(path: str):
        d = Dataset(get_rankings_from_file(path))
        d.name = name_file(path)
        return d

    def __get_rankings(self) -> List[List[List or Set[int or str]]]:
        return self.__rankings

    def __get_nb_elements(self) -> int:
        return len(self.__mapping_elements_id)

    def __get_path(self) -> str:
        return self.__name

    def __get_nb_rankings(self) -> int:
        return len(self.__rankings)

    def __get_is_complete(self) -> bool:
        return self.__is_complete

    def __get_with_ties(self) -> bool:
        return self.__with_ties

    def __get_elements(self) -> Set:
        return set(self.__mapping_elements_id)

    def __set_path(self, path: str):
        self.__name = path

    # number of elements
    nb_elements = property(__get_nb_elements)
    # number of rankings
    nb_rankings = property(__get_nb_rankings)
    # input rankings
    rankings = property(__get_rankings)
    # boolean: True iif all the rankings are on the same set of elements
    is_complete = property(__get_is_complete)
    # boolean: True iif there exists at least a bucket of size >= 2
    with_ties = property(__get_with_ties)
    # name of the dataset
    name = property(__get_path, __set_path)
    # universe of the rankings i.e. elements appearing in at least one ranking
    elements = property(__get_elements)

    def __str__(self) -> str:
        return str(self.rankings)

    def description(self) -> str:
        return "Dataset description:\n\telements:" + str(self.nb_elements) + "\n\trankings:" + str(self.nb_rankings) \
               + "\n\tcomplete:" \
               + str(self.is_complete) + "\n\twith ties: " + str(self.with_ties) + "\n\t" \
               + "rankings:\n" \
               + "\n".join("\t\tr"+str(i+1)+" = "+str(self.rankings[i]) for i in range(len(self.rankings)))

    # returns a numpy ndarray where positions[i][j] is the position of element i in ranking j. Missing: element: -1
    def get_positions(self, elements_id: Dict[str or int, int]) -> np.ndarray:
        n = self.nb_elements
        m = self.nb_rankings
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
        n = self.nb_elements
        m = self.nb_rankings
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
        return self.nb_elements < other.nb_elements or \
               (self.nb_elements == other.nb_elements and self.nb_rankings < other.nb_rankings)

    def __le__(self, other):
        return self.nb_elements <= other.nb_elements or \
               (self.nb_elements == other.nb_elements and self.nb_rankings <= other.nb_rankings)

    def __eq__(self, other):
        return self.nb_elements == other.nb_elements and self.nb_rankings == other.nb_rankings

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.nb_elements > other.nb_elements or \
               (self.nb_elements == other.nb_elements and self.nb_rankings > other.nb_rankings)

    def __ge__(self, other):
        return self.nb_elements >= other.nb_elements or \
               (self.nb_elements == other.nb_elements and self.nb_rankings >= other.nb_rankings)

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
            if self.__nb_elem_min <= dataset.nb_elements <= self.__nb_elem_max:
                if self.__nb_rankings_min <= dataset.nb_rankings <= self.__nb_rankings_max:
                    res.append(dataset)
        return res

    def __str__(self) -> str:
        return "nb elements between " + str(self.__nb_elem_min) + " and " + str(self.__nb_elem_max) + \
               "; nb rankings between " + str(self.__nb_rankings_min) + " and " + str(self.__nb_rankings_max)

    def __repr__(self) -> str:
        return self.__str__()
