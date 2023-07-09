from typing import List, Dict, Set, Tuple, Union, Iterator
from collections import Counter
import numpy as np
import copy
from corankco.utils import get_rankings_from_file, get_rankings_from_folder, write_rankings, name_file
from corankco.ranking import Ranking
from corankco.element import Element, PairwiseElementComparison
from corankco.scoringscheme import ScoringScheme


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
        rankings_final: List[Ranking] = []
        all_ints: bool = True
        for ranking in rankings:
            if not all_ints:
                break
            for bucket in ranking:
                if not all_ints:
                    break
                for element in bucket:
                    if isinstance(element, int):
                        continue
                    elif isinstance(element, str) and not element.isdigit():
                        all_ints = False
                    elif not element.can_be_int():
                        all_ints = False
                        break
        if all_ints:
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

        id_element = 0
        for key in nb_occur_elements_in_rankings.keys():
            self._mapping_element_id[key] = id_element
            self._mapping_id_element[id_element] = key
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
        d = Dataset([Ranking(ranking) for ranking in get_rankings_from_file(path)])
        d.name = name_file(path)
        return d

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
        return "Dataset description:\n\telements:" + str(self.nb_elements) + "\n\trankings:" + str(self.nb_rankings) \
            + "\n\tcomplete:" \
            + str(self.is_complete) + "\n\twithout ties: " + str(self.without_ties) + "\n\t" \
            + "rankings:\n" \
            + "\n".join("\t\tr" + str(i + 1) + " = " + str(self.rankings[i]) for i in range(len(self.rankings)))

    # returns a numpy ndarray where positions[i][j] is the position of element i in ranking j. Missing: element: -1
    def get_positions(self) -> np.ndarray:
        """

        :return: A (nb_elements, nb_rankings) numpy matrix where m[i][j] denotes the position of element i in ranking j
        position = -1 if element i is non-ranked in ranking j
        """
        positions: np.ndarray = np.zeros((self.nb_elements, self.nb_rankings)) - 1
        id_ranking: int = 0
        for ranking in self.rankings:
            id_bucket: int = 0
            for bucket in ranking:
                for elem in bucket:
                    positions[self.mapping_elem_id.get(elem)][id_ranking] = id_bucket
                id_bucket += 1
            id_ranking += 1
        return positions

    def penalties_relative_positions(self, scoring_scheme: ScoringScheme) -> Set[PairwiseElementComparison]:
        """
        Get a set of all pairs of elements with their costs of different relative positions under a Kemeny prism
        regarding the given ScoringScheme. Complexity: O(nb_elements * nb_elements * nb_rankings)
        Complexity: O(nb_rankings * nb_elements²)
        :param scoring_scheme: the ScoringScheme to use for the computation of the different relative costs
        :return: a Set of ElementComparison objects
        """
        res: Set[PairwiseElementComparison] = set()
        # for each element
        nb_elements: int = self.nb_elements
        positions: np.ndarray = self.get_positions()

        b_vector_numpy: np.ndarray = np.asarray(scoring_scheme.b_vector)
        t_vector_numpy: np.ndarray = np.asarray(scoring_scheme.t_vector)
        a_vector_numpy: np.ndarray = np.array(
            [b_vector_numpy[1], b_vector_numpy[0], b_vector_numpy[2], b_vector_numpy[4], b_vector_numpy[3],
             b_vector_numpy[5]])

        for id_el1 in range(0, nb_elements, 1):
            # for memoization: pos_el1 = the positions of elem id_el1 in the input rankings
            pos_el1: np.ndarray = positions[id_el1]

            # d: nb of rankings such that el1 is non-ranked
            d: int = np.count_nonzero(pos_el1 == -1)

            # for each other element
            for id_el2 in range(id_el1 + 1, nb_elements, 1):
                # a = nb of rankings such that el1 and el2 are both missing
                a: int = np.count_nonzero(pos_el1 + positions[id_el2] == -2)
                # b = number of rankings such that el1 and el2 have same position or are both missing
                b: int = np.count_nonzero(pos_el1 == positions[id_el2])
                # c = number of rankings such that el1 is ranked whereas el2 is non-ranked
                c: int = np.count_nonzero(positions[id_el2] == -1)
                # e = number of rankings such that el1 is before el2 or el1 is non-ranked whereas el2 is ranked
                e: int = np.count_nonzero(pos_el1 < positions[id_el2])

                # vector that contains for the two elements x and y the number of rankings such that respectively:
                # x < y, x > y, x and y are tied, x is the only ranked, y is the only ranked, x and y are non-ranked
                relative_positions: np.ndarray = np.array(
                    [e - d + a, self.nb_rankings - e - b - c + a, b - a, c - a, d - a, a])

                # cost to place el1 before el2 in consensus ranking
                x_before_y: float = np.vdot(relative_positions, b_vector_numpy)
                # cost to place el1 after el2 in consensus ranking
                x_after_y: float = np.vdot(relative_positions, a_vector_numpy)
                # cost to tie el1 and el2 in consensus ranking
                x_tied_y: float = np.vdot(relative_positions, t_vector_numpy)

                res.add(PairwiseElementComparison(self._mapping_id_element[id_el1], self._mapping_id_element[id_el2],
                                                  x_before_y, x_after_y, x_tied_y))
        return res

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
    def get_random_dataset_markov(nb_elem: int, nb_rankings: int, steps: int, complete: bool = False):
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

