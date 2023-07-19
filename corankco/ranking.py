"""
Module Ranking, containing one class (Ranking). A Ranking is defined as List of buckets, more formally a List of
disjoint sets of elements.
"""

from typing import List, Set, Union, Dict, Iterator
from random import shuffle, randint
import numpy as np
from corankco.element import Element
from corankco.utils import parse_ranking_with_ties_of_str


class Ranking:
    """
    A class to represent a ranking, defined as a List of disjoint Set of Elements

    """

    def __init__(self, buckets: Union[List[Set[int]], List[Set[str]], List[Set[Element]]]):
        """
        Constructs a Ranking instance with the given buckets.

        :param buckets: A list of buckets which are sets of Elements
        :type buckets: List[Set[Element]]
        :raises ValueError: If buckets are not disjoint

        """
        self._buckets: List[Set[Element]] = [{Element(x) for x in bucket} for bucket in buckets]

        # Initialize element_positions
        self._positions: Dict[Element, int] = {}

        # Check if buckets are disjoint and populate element_positions
        position: int = 1
        for bucket in buckets:
            for element in bucket:
                element_enc: Element = Element(element)
                if element_enc in self._positions:
                    raise ValueError(f"Element {element} found in multiple buckets. Buckets must be disjoint.")
                self._positions[element_enc] = position
            position += len(bucket)

    @classmethod
    def from_string(cls, ranking_str: str) -> 'Ranking':
        """
        Constructs a Ranking instance from a string representation.

        :param ranking_str: A string representation of a ranking
        :type ranking_str: str
        :return: A Ranking instance
        :rtype: Ranking

        """
        buckets: List[Set[Element]] = parse_ranking_with_ties_of_str(ranking_str)
        all_ints: bool = True
        for bucket in buckets:
            if not all_ints:
                break
            for elem in bucket:
                if not elem.can_be_int():
                    all_ints = False
                    break
        if all_ints:
            buckets_final: List[Set[Element]] = []
            for bucket in buckets:
                buckets_final.append({Element(int(str(elem))) for elem in bucket})
            return cls(buckets_final)
        return cls(buckets)

    @classmethod
    def from_file(cls, file_path: str) -> 'Ranking':
        """
        Constructs a Ranking instance from a file.

        :param file_path: The path to a file containing a ranking representation.
        :return: A Ranking instance.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            ranking_str: str = file.read()
        return cls.from_string(ranking_str)

    @property
    def buckets(self) -> List[Set[Element]]:
        """
        Returns the buckets of the ranking.

        :return: The buckets of the ranking
        :rtype: List[Set[Element]]

        """
        return self._buckets

    @property
    def positions(self) -> Dict[Element, int]:
        """
        Returns the positions of the elements in the ranking.

        :return: The positions of the elements in the ranking
        :rtype: Dict[Element, int]
        """
        return self._positions

    @property
    def domain(self) -> Set[Element]:
        """
        Returns the set of all elements in the Ranking.

        :return: A set of Elements which are the unique elements in the Ranking.

        """
        return set(self._positions.keys())

    @property
    def nb_elements(self) -> int:
        """
        Returns the number of unique elements in the Ranking.
        This is equivalent to the size of the domain of the Ranking.

        :return: An integer which is the number of unique elements in the Ranking.

        """
        return len(self.domain)

    def can_be_of_int(self) -> bool:
        """
        Returns true iif all the elements in the ranking can be converted to int

        :return: true iif all the elements in the ranking can be converted to int
        :rtype: bool

        """
        for bucket in self._buckets:
            for element in bucket:
                if not element.can_be_int():
                    return False
        return True

    def __len__(self) -> int:
        """
        Returns the number of buckets in the Ranking.

        This allows using the len() function on a Ranking object,
        yielding the number of buckets.

        Returns:
            An integer representing the number of buckets in the Ranking.
        """
        return len(self._buckets)

    def __iter__(self) -> Iterator[Set[Element]]:
        """
        Returns an iterator over the buckets in the Ranking.
        This allows the Ranking to be iterated over using a for loop,
        yielding each bucket in turn.

        return: An iterator over the buckets in the Ranking.

        """
        return iter(self._buckets)

    def __str__(self) -> str:
        """
        Returns a string representation of the Ranking instance.

        :return: A string representation of the Ranking instance
        :rtype: str

        """
        return str([set(bucket) for bucket in self._buckets])

    def __repr__(self) -> str:
        """
        Returns a string representation of the Ranking instance.

        :return: A string representation of the Ranking instance
        :rtype: str

        """
        return str([set(bucket) for bucket in self._buckets])

    def __getitem__(self, index: int) -> Set[Element]:
        """
        Retrieve the bucket at the given index.

        :param index: The index of the bucket to retrieve.
        :type index: int
        :returns: The bucket at the given index.
        :rtype: Set[Element]

        """
        return self.buckets[index]

    def __eq__(self, other):
        """
        Check if this Ranking is equal to another Ranking.

        :param other: Other Ranking to compare with.
        :returns: True if both Rankings are equal, False otherwise.
        :rtype: bool

        """
        if not isinstance(other, Ranking):
            return NotImplemented

        return self.buckets == other.buckets

    @staticmethod
    def uniform_permutations(nb_elem: int, nb_rankings: int) -> List['Ranking']:
        """
        Method to get a List of random uniform Rankings that are complete and without ties.

        :param nb_elem: the number of elements in the rankings
        :param nb_rankings: the number of rankings to generate
        :return: a list of random complete rankings without ties on {0, ..., n-1}

        """
        rankings: List[Ranking] = []
        for _ in range(nb_rankings):
            ranking_random: List[int] = list(range(1, nb_elem + 1))
            shuffle(ranking_random)
            ranking: List[Set[Element]] = [{Element(x)} for x in ranking_random]
            rankings.append(Ranking(ranking))
        return rankings

    @staticmethod
    def generate_rankings(nb_elements: int, nb_rankings: int, steps: int, complete=False) -> List['Ranking']:
        """

        Method to generate a List of nb_rankings rankings of nb_elements elements, possibly incomplete with ties.
        Each ranking is initially [{0}, {1}, ..., {n-1}], then modifications are done using a Markov chain.
        For each step from range 1 ... step parameter: an element is uniformly selected and may uniformly:
        - be added in the ranking if the element is currently non-ranked
        - be removed in the ranking if the element is currently ranked
        - be in a new bucket at the left of the current left neighbor bucket
        - be in a new bucket at the right of the current right neighbor bucket
        - be added in the current left neighbor bucket
        - be added in the current right neighbor bucket

        :param nb_elements: number of elements of the universe. Note that according to the steps of the Markov chain,

        the final list of rankings may have less than the given number of elements (if an element has been removed from

        all the input ranking)

        :param nb_rankings: the number of rankings to generate
        :param steps: the number of steps in the markov chain
        :param complete: does the final rankings need to be complete ? Default = False
        :return: a List of Ranking generated as described in the above description

        """
        # the list of rankings to return, as a raw list
        rankings_list: List[Ranking] = []

        # generates the list of rankings as a ndarray(nb_rankings, nb_elements)
        rankings: np.ndarray = np.zeros((nb_rankings, nb_elements), dtype=int)
        # initially, each ranking = [0, 1, ..., nb_elements-1]
        for i in range(nb_rankings):
            rankings[i] = np.arange(nb_elements)

        # each ranking is modified
        for ranking in rankings:
            missing_elements: Set[int] = set()

            # according to the number of steps in the markov chain
            if not complete:
                Ranking.__change_ranking_incomplete(ranking, steps, nb_elements, missing_elements)
            else:
                Ranking.__change_ranking_complete(ranking, steps, nb_elements)

            # when rankings are modified, they are returned as a List of Set of integers
            ranking_list: List[Set[Element]] = []
            nb_buckets: int = np.max(ranking) + 1
            for i in range(nb_buckets):
                ranking_list.append(set())
            for elem in range(nb_elements):
                bucket_elem: int = ranking[elem]
                if bucket_elem >= 0:
                    ranking_list[bucket_elem].add(Element(elem))
            if len(ranking_list) > 0:
                rankings_list.append(Ranking(ranking_list))
        return rankings_list

    @staticmethod
    def __add_left(ranking: np.ndarray, elem: int):
        # id of bucket of elem
        bucket_elem: int = ranking[elem]
        # if elem alone in its bucket: nothing to do. Otherwise
        # all the elements placed after or tied with elem have their bucket id +1
        if np.sum(ranking == bucket_elem) > 1:
            ranking[ranking >= bucket_elem] += 1
            ranking[elem] = bucket_elem

    @staticmethod
    def __add_right(ranking: np.ndarray, elem: int):
        # id of bucket of elem
        bucket_elem: int = ranking[elem]
        # if a most two elements in the bucket of elem: nothing to do. Otherwise
        # all the elements placed afterelem have their bucket id +1, same for elem
        if np.sum(ranking == bucket_elem) > 2:
            ranking[ranking > bucket_elem] += 1
            ranking[elem] = bucket_elem + 1

    @staticmethod
    def __change_left(ranking: np.ndarray, elem: int):
        bucket_elem: int = ranking[elem]
        size_bucket_elem: int = int(np.sum(ranking == bucket_elem))
        if bucket_elem != 0:
            if size_bucket_elem == 1:
                ranking[ranking > bucket_elem] -= 1
            ranking[elem] -= 1

    @staticmethod
    def __change_right(ranking: np.ndarray, elem: int):
        bucket_elem: int = ranking[elem]
        size_bucket_elem: int = int(np.sum(ranking == bucket_elem))
        size_bucket_following: int = int(np.sum(ranking == bucket_elem + 1))
        id_last_bucket: int = np.max(ranking)
        if bucket_elem != id_last_bucket and (size_bucket_elem > 1 or size_bucket_following > 1):
            ranking[elem] += 1
            if size_bucket_elem == 1:
                ranking[ranking > bucket_elem] -= 1

    @staticmethod
    def __remove_element(ranking: np.ndarray, elem: int):
        # id of bucket of elem
        bucket_elem: int = ranking[elem]
        size_bucket_elem: int = int(np.sum(ranking == bucket_elem))
        if size_bucket_elem == 1:
            ranking[ranking > bucket_elem] -= 1

        ranking[elem] = -1

    @staticmethod
    def __put_element_first(ranking: np.ndarray, elem: int):
        ranking[ranking >= 0] += 1
        ranking[elem] = 0

    @staticmethod
    def __step_element_incomplete(ranking: np.ndarray, elem: int, missing_elements: Set[int]):
        alea: int = randint(1, 5)
        if elem in missing_elements:
            if alea == 5:
                Ranking.__put_element_first(ranking, elem)
                missing_elements.remove(elem)
        else:
            if alea == 1:
                Ranking.__add_left(ranking, elem)
            elif alea == 2:
                Ranking.__add_right(ranking, elem)

            elif alea == 3:
                Ranking.__change_left(ranking, elem)

            elif alea == 4:
                Ranking.__change_right(ranking, elem)

            elif alea == 5:
                Ranking.__remove_element(ranking, elem)
                missing_elements.add(elem)

    @staticmethod
    def __change_ranking_complete(ranking: np.ndarray, steps: int, nb_elements: int):
        for _ in range(steps):
            Ranking.__step_element_complete(ranking, randint(0, nb_elements - 1))

    @staticmethod
    def __step_element_complete(ranking: np.ndarray, elem: int):
        alea: int = randint(1, 4)
        if alea == 1:
            Ranking.__add_left(ranking, elem)
        elif alea == 2:
            Ranking.__add_right(ranking, elem)

        elif alea == 3:
            Ranking.__change_left(ranking, elem)

        elif alea == 4:
            Ranking.__change_right(ranking, elem)

    @staticmethod
    def __change_ranking_incomplete(ranking: np.ndarray, steps: int, nb_elements: int, missing_elements: Set):
        for _ in range(steps):
            Ranking.__step_element_incomplete(ranking, randint(0, nb_elements - 1), missing_elements)
