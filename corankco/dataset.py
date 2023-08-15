"""
Module providing the Dataset class, and a DatasetSelector class to filter datasets according to the number of rankings
and/or elements. A Dataset is basically a list of rankings.
"""

from typing import List, Dict, Set, Tuple, Union, Iterator
from collections import Counter
import copy
import numpy as np
from corankco.utils import get_rankings_from_file, get_rankings_from_folder, write_rankings, name_file
from corankco.ranking import Ranking
from corankco.element import Element


class EmptyDatasetException(Exception):
    """Custom exception for empty dataset"""


class Dataset:
    """
    Class representing a dataset containing rankings.

    :param rankings: The rankings in the dataset.
    :type rankings: List[Ranking]
    :param name: Name of the dataset. Defaults to "None".
    :type name: str, optional
    :param repetitions: A list of integers indicating the number of occurrences for each ranking.
                        If set, its length must match that of `rankings`.
    :type repetitions: List[int], optional
    :param weights: A list of floats indicating the weight of each ranking.
                    If set, its length must match that of `rankings`.
    :type weights: List[float], optional

    Note:
        If both `repetitions` and `weights` are set, the ranking at index k is repeated `repetitions[k]` times with the

        same weight `weights[k]`.
    """

    def __init__(self, rankings: List[Ranking], name: str = "None",
                 repetitions: List[int] = None, weights: List[float] = None):
        """
        Constructor for the Dataset class.

        :param rankings: Rankings in the dataset.
        :type rankings: List[Ranking]
        :param name: Name of the dataset. Defaults to "None".
        :type name: str, optional
        :param repetitions: A list of integers indicating the number of occurrences for each ranking.
                            Its length must match that of `rankings` if set.
        :type repetitions: List[int], optional
        :param weights: A list of floats indicating the weight of each ranking.
                        Its length must match that of `rankings` if set.
        :type weights: List[float], optional
        """

        self._mapping_element_id: Dict[Element, int] = {}
        self._mapping_id_element: Dict[int, Element] = {}

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
    def from_raw_list(cls, rankings: List[Union[List[Set[int]], List[Set[str]], List[Set[Element]]]],
                      name: str = "") -> 'Dataset':
        """
        Create a Dataset from a raw list of rankings.

        :param rankings: A list of rankings.
        :type rankings: List[Union[List[Set[int]], List[Set[str]], List[Set[Element]]]]
        :param name: The name of the dataset.
        :type name: str, optional
        :return: A new Dataset object.
        :rtype: Dataset
        """
        dataset = cls([Ranking(ranking) for ranking in rankings])
        dataset.name = name
        return dataset

    @classmethod
    def _from_raw_list_with_elements(cls, rankings: List[List[Set[Element]]], name: str = "") -> 'Dataset':
        """
        Create a Dataset from a raw list of rankings with elements.

        :param rankings: A list of rankings.
        :param name: The name of the dataset.
        :return: A new Dataset object.
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
        rankings_final: List[Ranking] = []

        if Dataset._all_integers(rankings):
            for ranking in rankings:
                ranking_final: List[Set[Element]] = []
                for bucket in ranking:
                    ranking_final.append({Element(int(str(e))) for e in bucket})
                rankings_final.append(Ranking(ranking_final))
        else:
            for ranking in rankings:
                ranking_final: List[Set[Element]] = []
                for bucket in ranking:
                    ranking_final.append({Element(str(e)) for e in bucket})
                rankings_final.append(Ranking(ranking_final))
        # check if rankings are complete or not, and with or without ties

        # now, checking if dataset is complete or not, with or without ties
        without_ties: bool = True
        complete: bool = True

        # dataset is complete iif each element is present as many times as the nb of rankings
        nb_occur_elements_in_rankings: Dict[Element, int] = {}
        for ranking in rankings_final:
            for bucket in ranking:
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

        id_element: int = 0
        for key, _ in nb_occur_elements_in_rankings.items():
            self._mapping_element_id[key] = id_element
            self._mapping_id_element[id_element] = key
            id_element += 1
            if nb_occur_elements_in_rankings[key] != len(rankings_final):
                complete = False
        return rankings_final, complete, without_ties

    @staticmethod
    def _all_integers(rankings: List[Ranking]) -> bool:
        """

        :return: True iif all the elements of the dataset can be integers
        """
        for ranking in rankings:
            for bucket in ranking:
                for element in bucket:
                    if isinstance(element, str) and not element.isdigit():
                        return False
                    if isinstance(element, Element) and not element.can_be_int():
                        return False
        # If we have checked all elements and none have returned False, then we can return True
        return True

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
        for element in self.universe:
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
            self._mapping_element_id.pop(element_to_remove)
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
        dataset: Dataset = Dataset([Ranking(ranking) for ranking in get_rankings_from_file(path)])
        dataset.name = name_file(path)
        return dataset

    @property
    def rankings(self) -> List[Ranking]:
        """
        Get the rankings from the Dataset.

        :return: The list of rankings in this Dataset object.
        :rtype: List[Ranking]
        """
        return self._rankings

    @property
    def nb_elements(self) -> int:
        """
        Get the total number of elements that appear in at least one ranking of the Dataset.

        :return: The total number of elements in the Dataset.
        :rtype: int
        """
        return len(self._mapping_element_id)

    @property
    def name(self) -> str:
        """
        Method to get the name of the dataset.

        :return: Returns the name of the dataset.
        :rtype: str
        """
        return self._name

    @property
    def nb_rankings(self) -> int:
        """
        Method to get the number of rankings of the dataset.

        :return: Returns the number of rankings.
        :rtype: int
        """
        return len(self._rankings)

    @property
    def is_complete(self) -> bool:
        """
        Method to check if the dataset is complete that is if all the rankings of the dataset have the same domain.

        :return: Returns True if the object is complete, False otherwise.
        :rtype: bool
        """
        return self._is_complete

    @property
    def without_ties(self) -> bool:
        """
        Method to check if the dataset is a list of rankings without ties
        :return: Returns True iif all the rankings of the dataset are without ties
        :rtype: bool
        """
        return self._without_ties

    @property
    def universe(self) -> Set:
        """
        Method to get the set of elements that appear in at least one input ranking of the dataset.

        :return: Returns a set of elements.
        :rtype: Set
        """
        return set(self._mapping_element_id)

    @property
    def mapping_elem_id(self) -> Dict[Element, int]:
        """
        Method to get the mapping element -> unique int ID for each element of the universe of the dataset

        :return: Returns a dictionary that associates for each element of the universe a unique int ID.
        :rtype: Dict[Element, int]
        """
        return self._mapping_element_id

    @property
    def mapping_id_elem(self) -> Dict[int, Element]:
        """
        Method to get the mapping element -> unique int ID for each element of the universe of the dataset

        :return: Returns a dictionary that associates for each element of the universe a unique int ID.
        :rtype: Dict[Element, int]
        """
        return self._mapping_id_element

    @name.setter
    def name(self, path: str):
        """
        Method to set the name of the dataset.

        :param path: The new name of the dataset.
        :type path: str
        """
        self._name = path

    def __str__(self) -> str:
        """
        A string representation of the Dataset as a list of rankings
        :return: the string representing the list of input rankings
        """
        return str(self.rankings)

    def description(self) -> str:
        """
        :return: A complete description of the Dataset object containing all the available information
        """
        rankings = '\n'.join(f"\t\tr{i + 1} = {ranking}" for i, ranking in enumerate(self.rankings))

        description = (f"Dataset description:\n"
                       f"\tname: {self.name}\n"
                       f"\telements: {self.nb_elements}\n"
                       f"\trankings: {self.nb_rankings}\n"
                       f"\tcomplete: {self.is_complete}\n"
                       f"\twithout ties: {self.without_ties}\n"
                       f"\trankings:\n"
                       f"{rankings}")

        return description

    # returns a numpy ndarray where positions[i][j] is the position of element i in ranking j. Missing: element: -1
    def get_positions(self) -> np.ndarray:
        """

        :return: A (nb_elements, nb_rankings) numpy matrix where m[i][j] denotes the position of element i in ranking j
                 position = -1 if element i is non-ranked in ranking j
        """
        positions: np.ndarray = np.full((self.nb_elements, self.nb_rankings), -1, dtype=np.int32)
        id_ranking: int = 0
        for ranking in self.rankings:
            for elem, pos in ranking.positions.items():
                positions[self.mapping_elem_id.get(elem)][id_ranking] = pos - 1
            id_ranking += 1
        return positions

    def get_bucket_ids(self) -> np.ndarray:
        """
        :return: A (nb_elements, nb_rankings) numpy matrix where m[i][j] denotes the bucket id of element i in ranking j
                 position = -1 if element i is non-ranked in ranking j
        """
        bucket_ids: np.ndarray = np.full((self.nb_elements, self.nb_rankings), -1, dtype=np.int32)

        for ranking_idx, ranking in enumerate(self.rankings):
            for bucket_id, bucket in enumerate(ranking):
                for elem in bucket:
                    bucket_ids[self.mapping_elem_id.get(elem)][ranking_idx] = bucket_id

        return bucket_ids

    def unified_rankings(self) -> List[Ranking]:
        """
        Get a unified version of the dataset as a List of Ranking objects, that is a list of the input rankings such
        that for each ranking r, all the elements of the universe non-ranked in r are added in a unifying bucket at the
        end of r.
        :return: the unified rankings of the Dataset within a new Ranking List

        """
        copy_rankings: List[Ranking] = copy.deepcopy(self.rankings)
        all_elements: Set[Element] = set(self._mapping_element_id.keys())

        for ranking in copy_rankings:
            missing_elements: Set[Element] = all_elements - ranking.domain
            if missing_elements:
                ranking.buckets.append(missing_elements)

        return copy_rankings

    def unified_dataset(self):
        """
        Get a new Dataset object, representing the unified version of the instance dataset.
        In the returned dataset, for each input ranking r, all the elements of the universe non-ranked in r are added
        in a unifying bucket at the end of r.
        :return: a new Dataset object representing the unified version of the current instance
        """
        return Dataset(self.unified_rankings())

    def sub_problem_from_elements(self, elements_to_keep: Set[Element]) -> 'Dataset':
        """
        Generates a sub-problem Dataset by projecting the original Dataset on a given set of elements.

        The resulting Dataset only includes the rankings that contain at least one of the elements from
        the 'elements_to_keep' set. Similarly, within each ranking, only buckets that contain at least one
        of the elements from the 'elements_to_keep' set are kept.

        :param elements_to_keep: A set of elements which the sub-problem should be based on.
        :type elements_to_keep: Set[Element]

        :return: A Dataset representing the sub-problem, which only includes the elements from 'elements_to_keep' set.
        :rtype: Dataset
        """

        projected_rankings = [
            Ranking([
                bucket.intersection(elements_to_keep)
                for bucket in ranking
                if bucket.intersection(elements_to_keep)
            ])
            for ranking in self.rankings
            if any(bucket.intersection(elements_to_keep) for bucket in ranking)
        ]
        return Dataset(projected_rankings)

    def sub_problem_from_ids(self, id_elements_to_keep: Set[int]) -> 'Dataset':
        """
        Generates a sub-problem Dataset by projecting the original Dataset on a given set of int IDs of elements.

        The resulting Dataset only includes the rankings that contain at least one of the elements from
        the 'elements_to_keep' set. Similarly, within each ranking, only buckets that contain at least one
        of the elements from the 'elements_to_keep' set are kept.

        :param id_elements_to_keep: A set of elements which the sub-problem should be based on.
        :type id_elements_to_keep: Set[int]

        :return: A Dataset representing the sub-problem which only includes the elements from 'id_elements_to_keep' set.
        :rtype: Dataset
        """

        return self.sub_problem_from_elements(set(self._mapping_id_element[id_elem] for id_elem in id_elements_to_keep))

    def write(self, path) -> None:
        """
        Stores the input rankings of the dataset in a file
        :param path: the path to store the dataset
        :return: None
        """
        rankings_as_list_of_sets = [ranking.buckets for ranking in self.rankings]
        write_rankings(rankings_as_list_of_sets, path)

    @staticmethod
    def get_uniform_permutation_dataset(nb_elem: int, nb_rankings: int):
        """
        Get a Dataset of nb_elem elements and nb_rankings complete rankings without ties
        where each ranking is uniformly generated
        :param nb_elem: the number of wanted elements for the dataset
        :param nb_rankings: the number of rankings for the dataset
        :return: a new Dataset instance whose rankings are uniformly generated complete rankings without ties
        """
        return Dataset(Ranking.uniform_permutations(nb_elem, nb_rankings))

    @staticmethod
    def get_random_dataset_markov(nb_elem: int, nb_rankings: int, steps: int, complete: bool = False) -> 'Dataset':
        """
        Get a Dataset generated using a Markov chain. Note that if complete is set to false, the return dataset
        may contain fewer elements than initially wanted if one or more elements have been removed from all the rankings
        during the markov walking
        :param nb_elem: the number of elements in the wanted dataset
        :param nb_rankings: the number of rankings in the wanted dataset
        :param steps: the number of steps in the Markov chain for each ranking to generate
        :param complete: true iif the wanted dataset must be complete that is if all the elements must be ranked in all
        the rankings
        :return: A Dataset generated using a Markov chain, see details in corankco.rankingsgeneration.rankingsgenerate
        """
        return Dataset(Ranking.generate_rankings(nb_elem, nb_rankings, steps, complete))

    @staticmethod
    def get_datasets_from_folder(path_folder: str) -> List['Dataset']:
        """
        Get a List of Dataset, one by file of the folder path
        :param path_folder: the path of the folder containing the datasets
        :return: a List containing one Dataset by dataset file in the input folder path
        """
        return [Dataset._from_raw_list_with_elements
                (rankings, name=file_path) for rankings, file_path in get_rankings_from_folder(path_folder)]

    def __repr__(self):
        """

        :return: The string representation of the rankings defining the Dataset object.
        """
        return str(self.rankings)

    def contains_element(self, element: Union[str, int]) -> bool:
        """

        :param element: the element to find
        :return: true iif the target element is ranked in at least one input ranking of the dataset
        """
        return element in self.universe

    def __iter__(self) -> Iterator[Ranking]:
        """

        Returns an iterator over the rankings buckets in the Dataset.
        This allows the Dataset to be iterated over using a for loop,
        yielding each ranking in turn.
        :return: An iterator over the rankings in the Dataset.        """

        return iter(self._rankings)

    def __getitem__(self, index: int) -> Ranking:
        """
        Retrieve the ranking at the given index.

        :param index: The index of the ranking to retrieve.
        :type index: int
        :returns: The ranking at the given index.
        :rtype: Ranking
        """
        return self.rankings[index]

    def __eq__(self, other):
        """
        Check if this Dataset is equivalent to another Dataset, regardless of the order of the Rankings.

        :param other: Other Dataset to compare with.
        :returns: True if both Datasets are equivalent, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Dataset):
            return NotImplemented

        self_str_rankings: List[str] = [str(ranking).strip().replace(" ", "") for ranking in self.rankings]
        other_str_rankings: List[str] = [str(ranking).strip().replace(" ", "") for ranking in other.rankings]

        return Counter(self_str_rankings) == Counter(other_str_rankings)


class DatasetSelector:
    """
    Class usable to filter datasets according to their number of elements and / or rankings
    """

    def __init__(self,
                 nb_elem_min: int = 0,
                 nb_elem_max: Union[int, float] = float('inf'),
                 nb_rankings_min: int = 0,
                 nb_rankings_max: Union[int, float] = float('inf')):
        """

        :param nb_elem_min: the min number of elements of the datasets to filter. Default = 0
        :param nb_elem_max: the max number of elements of the datasets to filter. Default = inf
        :param nb_rankings_min: the min number of rankings of the datasets to filter. Default = 0
        :param nb_rankings_max: the max number of rankings of the datasets to filter. Default = inf
        """
        self._nb_elem_min: int = nb_elem_min
        self._nb_elem_max: Union[int, float] = nb_elem_max
        self._nb_rankings_min: int = nb_rankings_min
        self._nb_rankings_max: Union[int, float] = nb_rankings_max

    @property
    def nb_elem_min(self) -> int:
        """

        :return: The value of the attribute, that is the minimal number of elements to retain a dataset
        """
        return self._nb_elem_min

    @property
    def nb_rankings_min(self) -> int:
        """

         :return: The value of the attribute, that is the minimal number of rankings to retain a dataset
         """
        return self._nb_rankings_min

    @property
    def nb_elem_max(self) -> Union[int, float]:
        """

         :return: The value of the attribute, that is the maximal number of elements to retain a dataset
         """
        return self._nb_elem_max

    @property
    def nb_rankings_max(self) -> Union[int, float]:
        """

         :return: The value of the attribute, that is the maximal number of rankings to retain a dataset
         """
        return self._nb_rankings_max

    def select_datasets(self, list_datasets: List[Dataset]) -> List[Dataset]:
        """
        Given a list of Dataset objects, returns the List of Dataset references that fit with the filter
        :param list_datasets: the list of datasets to filter
        :return: the list l of Dataset references such that d in l iif:
        * self.nb_elem_min <= d.nb_elements <= self.nb_elem_max
        * self.nb_rankings_min <= d.nb_rankings <= self.nb_rankings_max
        """
        res: List[Dataset] = []
        for dataset in list_datasets:
            if self._nb_elem_min <= dataset.nb_elements <= self._nb_elem_max:
                if self._nb_rankings_min <= dataset.nb_rankings <= self._nb_rankings_max:
                    res.append(dataset)
        return res

    def __str__(self) -> str:
        """

        :return: a String representation of the object, containing the values of the attributes of the class
        """
        return "nb elements between " + str(self._nb_elem_min) + " and " + str(self._nb_elem_max) + \
            "; nb rankings between " + str(self._nb_rankings_min) + " and " + str(self._nb_rankings_max)

    def __repr__(self) -> str:
        """

        :return: a String representation of the object, containing the values of the attributes of the class
        """
        return self.__str__()
