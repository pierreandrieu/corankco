from typing import List, Dict, Set, Tuple, Union
import numpy as np
import copy
from corankco.utils import get_rankings_from_file, get_rankings_from_folder, write_rankings, name_file
from corankco.rankingsgeneration.rankingsgenerate import create_rankings, uniform_permutations
from corankco.ranking import Ranking
from corankco.element import Element


class EmptyDatasetException(Exception):
    """Custom exception for empty dataset"""


class Dataset:
    """
    Class representing a dataset containing rankings.

    :param rankings: Rankings in the dataset.
    :type rankings: list of Ranking
    :param name: Name of the dataset.
    :type name: str, optional
    """

    def __init__(self, rankings: List[Ranking], name: str = ""):
        """
        Constructor for the Dataset class.

        :param rankings: Rankings in the dataset.
        :type rankings: list of Ranking
        :param name: Name of the dataset.
        :type name: str, optional
        """
        self._mapping_elements_id: Dict[Element, int] = {}
        # analyze the input rankings
        self._rankings, self._is_complete, self._without_ties = self._analyse_rankings(rankings)
        self._name: str = name

    @classmethod
    def from_file(cls, path: str) -> 'Dataset':
        """
        Create a Dataset from a file containing rankings.

        :param path: The path to the file.
        :type path: str
        :return: A new Dataset object.
        :rtype: Dataset
        """
        dataset = cls([Ranking(ranking) for ranking in get_rankings_from_file(path)])
        dataset.name = name_file(path)
        return dataset

    @classmethod
    def from_raw_list(cls, rankings: List[List[Set[Union[int, str]]]], name: str = "") -> 'Dataset':
        """
        Create a Dataset from a raw list of rankings.

        :param rankings: A list of rankings.
        :type rankings: List[List[Set[Union[int, str]]]]
        :param name: The name of the dataset.
        :type name: str, optional
        :return: A new Dataset object.
        :rtype: Dataset
        """
        dataset = cls([Ranking.from_list(ranking) for ranking in rankings])
        dataset.name = name
        return dataset

    @classmethod
    def _from_raw_list_with_elements(cls, rankings: List[List[Set[Element]]], name: str = "") -> 'Dataset':
        """
        Create a Dataset from a raw list of rankings with elements.

        :param rankings: A list of rankings.
        :type rankings: List[List[Set[Element]]]
        :param name: The name of the dataset.
        :type name: str, optional
        :return: A new Dataset object.
        :rtype: Dataset
        """
        dataset = cls([Ranking(ranking) for ranking in rankings])
        dataset.name = name
        return dataset

    def _analyse_rankings(self, rankings: List[Ranking]) -> Tuple[List[Ranking], bool, bool]:
        """
        Analyze the input rankings to check if they are complete, with or without ties.

        :param rankings: Rankings to be analyzed.
        :type rankings: list of Ranking
        :return: A tuple containing the final list of rankings, a boolean indicating if the rankings are complete,
                 and another boolean indicating if the rankings are without ties.
        :rtype: tuple
        """
        if len(rankings) == 0:
            raise EmptyDatasetException("There must be at least one ranking")

        # check if all elements are integers. If yes, all str are converted to integers
        rankings_final = copy.deepcopy(rankings)
        # check if rankings are complete or not, and with or without ties

        # now, checking if dataset is complete or not, with or without ties
        without_ties: bool = True
        complete: bool = True

        # dataset is complete iif each element is present as many times as the nb of rankings
        nb_occur_elements_in_rankings: Dict[Element, int] = {}
        for ranking in rankings_final:
            nb_elements = 0
            for bucket in ranking:
                nb_elements += len(bucket)
                if len(bucket) > 1:
                    without_ties = False
                for element in bucket:
                    if element not in nb_occur_elements_in_rankings:
                        nb_occur_elements_in_rankings[element] = 1
                    else:
                        nb_occur_elements_in_rankings[element] += 1

        # forbidden to have no element
        if len(nb_occur_elements_in_rankings) == 0:
            raise EmptyDatasetException("No elements found in input rankings")

        id_element = 0
        for key in nb_occur_elements_in_rankings.keys():
            self._mapping_elements_id[key] = id_element
            id_element += 1
            if nb_occur_elements_in_rankings[key] != len(rankings_final):
                complete = False
        return rankings_final, complete, without_ties
    def remove_empty_rankings(self):
        """
        Remove empty rankings from the dataset.

        :return: None
        """
        rankings_new: List[Ranking] = [ranking for ranking in self.rankings if len(ranking) > 0]
        self._rankings, self._is_complete, self._without_ties = self._analyse_rankings(rankings_new)

    def remove_elements_rate_presence_lower_than(self, rate_presence: float):
        """
        Remove elements whose rate of presence in the rankings is lower than the provided threshold.

        :param rate_presence: Threshold below which elements are removed.
        :type rate_presence: float
        :return: None
        """
        # associate for each element e the nb of rankings r of the dataset such that e in dom(r)
        presence: Dict[Element, int] = {}
        for element in self.elements:
            presence[element] = 0
        for ranking in self._rankings:
            for bucket in ranking:
                for element in bucket:
                    presence[element] += 1
        elements_to_remove = set()
        # all the elements whose rate of presence is lower than the minimal rate of presence
        # required will be removed
        for element, nb_rankings_present in presence.items():
            if nb_rankings_present / self.nb_rankings < rate_presence:
                elements_to_remove.add(element)
        self.remove_elements(elements_to_remove)

    def remove_elements(self, elements_to_remove: Set):
        """
        Remove elements from all rankings in the dataset.

        :param elements_to_remove: Set of elements to remove.
        :type elements_to_remove: Set[Element]
        :return: None
        """

        # operation of projection
        new_rankings: List[Ranking] = []
        for old_ranking in self.rankings:
            new_ranking = []
            for old_bucket in old_ranking:
                new_bucket: Set[Element] = set()
                for old_element in old_bucket:
                    if old_element not in elements_to_remove:
                        new_bucket.add(old_element)
                if len(new_bucket) > 0:
                    new_ranking.append(new_bucket)
            if len(new_ranking) > 0:
                new_rankings.append(Ranking(new_ranking))
        # the mapping element / id must be updated by removing the elements that should be removed
        for element_to_remove in elements_to_remove:
            self._mapping_elements_id.pop(element_to_remove)
        # the features of the dataset must be re-computed after removing some elements
        self._rankings, self._is_complete, self._without_ties = self._analyse_rankings(new_rankings)

    @staticmethod
    def get_dataset_from_file(path: str) -> 'Dataset':
        """
        Read a file of rankings and return a Dataset object.

        :param path: The path to the ranking file to read.
        :type path: str
        :return: A Dataset object containing the read rankings.
        :rtype: Dataset
        """
        d = Dataset([Ranking(ranking) for ranking in get_rankings_from_file(path)])
        d.name = name_file(path)
        return d

    def _get_rankings(self) -> List[Ranking]:
        """
        Get the rankings from the Dataset.

        :return: The list of rankings in this Dataset object.
        :rtype: List[Ranking]
        """
        return self._rankings

    def _get_nb_elements(self) -> int:
        """
        Get the total number of elements that appear in at least one ranking of the Dataset.

        :return: The total number of elements in the Dataset.
        :rtype: int
        """
        return len(self._mapping_elements_id)

    def _get_name(self) -> str:
        """
        Method to get the name of the dataset.

        :return: Returns the name of the dataset.
        :rtype: str
        """
        return self._name

    def _get_nb_rankings(self) -> int:
        """
        Method to get the number of rankings of the dataset.

        :return: Returns the number of rankings.
        :rtype: int
        """
        return len(self._rankings)

    def _get_is_complete(self) -> bool:
        """
        Method to check if the dataset is complete that is if all the rankings of the dataset have the same domain.

        :return: Returns True if the object is complete, False otherwise.
        :rtype: bool
        """
        return self._is_complete

    def _get_without_ties(self) -> bool:
        """
        Method to check if the dataset is a list of rankings without ties
        :return: Returns True iif all the rankings of the dataset are without ties
        :rtype: bool
        """
        return self._without_ties

    def _get_elements(self) -> Set:
        """
        Method to get the set of elements that appear in at least one input ranking of the dataset.

        :return: Returns a set of elements.
        :rtype: Set
        """
        return set(self._mapping_elements_id)

    def _set_name(self, path: str):
        """
        Method to set the name of the dataset.

        :param path: The new name of the dataset.
        :type path: str
        """
        self._name = path

    # number of elements
    nb_elements = property(_get_nb_elements)
    # number of rankings
    nb_rankings = property(_get_nb_rankings)
    # input rankings
    rankings = property(_get_rankings)
    # boolean: True iif all the rankings are on the same set of elements
    is_complete = property(_get_is_complete)
    # boolean: True iif there exists at least a bucket of size >= 2
    without_ties = property(_get_without_ties)
    # name of the dataset
    name = property(_get_name, _set_name)
    # universe of the rankings i.e. elements appearing in at least one ranking
    elements = property(_get_elements)

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

    def unified_rankings(self) -> List[Ranking]:
        copy_rankings = copy.deepcopy(self.rankings)
        all_elements = set(self._mapping_elements_id.keys())

        for ranking in copy_rankings:
            missing_elements = all_elements - ranking.domain()
            if missing_elements:
                ranking.buckets.append(missing_elements)

        return copy_rankings

    def unified_dataset(self):
        return Dataset(self.unified_rankings())

    def write(self, path):
        rankings_as_list_of_sets = [ranking.buckets for ranking in self.rankings]
        write_rankings(rankings_as_list_of_sets, path)

    @staticmethod
    def get_uniform_dataset(nb_elem: int, nb_rankings: int):
        return Dataset.from_raw_list(uniform_permutations(nb_elem, nb_rankings))

    @staticmethod
    def get_random_dataset_markov(nb_elem: int, nb_rankings: int, step, complete: bool = False):
        return Dataset(create_rankings(nb_elem, nb_rankings, step, complete))

    @staticmethod
    def get_datasets_from_folder(path_folder: str) -> List:
        return [Dataset._from_raw_list_with_elements
                (rankings, name=file_path) for rankings, file_path in get_rankings_from_folder(path_folder)]

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
        self._nb_elem_min = nb_elem_min
        self._nb_elem_max = nb_elem_max
        self._nb_rankings_min = nb_rankings_min
        self._nb_rankings_max = nb_rankings_max

    def _get_nb_elem_min(self) -> int:
        return self._nb_elem_min

    def _get_nb_rankings_min(self) -> int:
        return self._nb_rankings_min

    def _get_nb_elem_max(self) -> int or float:
        return self._nb_elem_max

    def _get_nb_rankings_max(self) -> int or float:
        return self._nb_rankings_max

    nb_elem_max = property(_get_nb_elem_max)
    nb_elem_min = property(_get_nb_elem_min)
    nb_rankings_max = property(_get_nb_rankings_max)
    nb_rankings_min = property(_get_nb_rankings_min)

    def select_datasets(self, list_datasets: List) -> List:
        res = []
        for dataset in list_datasets:
            if self._nb_elem_min <= dataset.nb_elements <= self._nb_elem_max:
                if self._nb_rankings_min <= dataset.nb_rankings <= self._nb_rankings_max:
                    res.append(dataset)
        return res

    def __str__(self) -> str:
        return "nb elements between " + str(self._nb_elem_min) + " and " + str(self._nb_elem_max) + \
               "; nb rankings between " + str(self._nb_rankings_min) + " and " + str(self._nb_rankings_max)

    def __repr__(self) -> str:
        return self.__str__()
