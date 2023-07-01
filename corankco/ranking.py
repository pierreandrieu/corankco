from typing import List, Set, Union, Dict, Iterator
from corankco.element import Element
from corankco.utils import parse_ranking_with_ties_of_str


class Ranking:
    """
    A class to represent a ranking.

    :ivar _buckets: A list of buckets which are sets of Elements.
    """

    def __init__(self, buckets: List[Set[Element]]):
        """
        Constructs a Ranking instance with the given buckets.

        :param buckets: A list of buckets which are sets of Elements
        :type buckets: List[Set[Element]]
        :raises ValueError: If buckets are not disjoint
        """
        self._buckets: List[Set[Element]] = buckets

        # Initialize element_positions
        self._positions: Dict[Element, int] = dict()

        # Check if buckets are disjoint and populate element_positions
        position: int = 1
        for bucket in buckets:
            for element in bucket:
                if element in self._positions:
                    raise ValueError(f"Element {element} found in multiple buckets. Buckets must be disjoint.")
                self._positions[element] = position
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
        return cls(buckets)

    @classmethod
    def from_list(cls, ranking_list: List[Set[Union[int, str]]]) -> 'Ranking':
        """
        Constructs a Ranking instance from a list of elements.

        :param ranking_list: A list of elements representing a ranking
        :type ranking_list: List[Union[int, str]]
        :return: A Ranking instance
        :rtype: Ranking
        """
        buckets: List[Set[Element]] = [set([Element(elem) for elem in bucket]) for bucket in ranking_list]
        return cls(buckets)

    @classmethod
    def from_file(cls, file_path: str) -> 'Ranking':
        """
        Constructs a Ranking instance from a file.

        :param file_path: The path to a file containing a ranking representation
        :type file_path: str
        :return: A Ranking instance
        :rtype: Ranking
        """
        with open(file_path, 'r') as f:
            ranking_str: str = f.read()
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

        This is equivalent to the keys of the attribute 'positions'.

        Returns:
            A set of Elements which are the unique elements in the Ranking.
        """
        return set(self._positions.keys())

    @property
    def nb_elements(self) -> int:
        """
        Returns the number of unique elements in the Ranking.

        This is equivalent to the size of the domain of the Ranking.

        Returns:
            An integer which is the number of unique elements in the Ranking.
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

    """"
    def to_int(self) -> 'Ranking':
        print("to_int")
        int_repr = []
        for bucket in self._buckets:
            bucket_int: Set[int] = set()
            for element in bucket:
                print("elem = " + str(element) + " " + str(element.value) + " " + str(element.type))
                if element.type == str and element.value.isdigit():
                    print(" entree if ")
                    bucket_int.add(int(element.value))
                    print(" fin if ")
                else:
                    print("probleme with elem " + str(element))
                    raise ValueError(f"Cannot convert {element.value} to int")
            int_repr.append(bucket_int)
        print("fin")
        return Ranking.from_list(int_repr)
    """
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

        Returns:
            An iterator over the buckets in the Ranking.
        """
        return iter(self._buckets)

    def __str__(self) -> str:
        """
        Returns a string representation of the Ranking instance.

        :return: A string representation of the Ranking instance
        :rtype: str
        """
        return str([{elem.value for elem in bucket} for bucket in self._buckets])

    def __repr__(self) -> str:
        """
        Returns a string representation of the Ranking instance.

        :return: A string representation of the Ranking instance
        :rtype: str
        """
        return str([{elem.value for elem in bucket} for bucket in self._buckets])

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
