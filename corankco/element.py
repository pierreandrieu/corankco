"""
This module contains the Element class used to encapsulate an element to be ranked.
An element is defined as an int or a string.
"""

from typing import Union, Type


class Element:
    """
    A class to represent an element of a ranking.

    :param value: the value of the element, either an integer or a string
    :type value: Union[int, str]
    """

    def __init__(self, value: Union[int, str, 'Element']):
        """
        Constructs an Element instance with the given value.

        :param value: The value of the element, either an integer or a string
        :type value: Union[int, str]
        :raises TypeError: If value is not an integer or a string
        """
        if isinstance(value, int):
            self._type = int
            self._value = value
        elif isinstance(value, str):
            self._type = str
            self._value = value
        elif isinstance(value, Element):
            self._type = value.type
            self._value = value.value
        else:
            raise TypeError("Value must be int, str or Element ", type(value), " found")

    @property
    def value(self) -> Union[int, str]:
        """
        returns the value of the instance
        :return: value of the instance
        :rtype: Union[int, str]
        """
        return self._value

    @property
    def type(self) -> Type:
        """
        returns the type of the instance
        :return: type of the instance
        :rtype: Type
        """
        return self._type

    def can_be_int(self):
        """

        :return: True iif the value of Element object is an int or a str that can be converted to int
        """
        return self._type == int or self._value.isdigit()

    def __eq__(self, other: Union['Element', str, int]) -> bool:
        """
        Checks if two elements are equal.

        :param other: Another element to compare.
        :type other: Element
        :return: True if both elements have the same value, False otherwise.
        :rtype: bool
        """
        if isinstance(other, Element):
            return self.type == other.type and self.value == other.value
        if isinstance(other, str):
            return self.type == str and self.value == other
        if isinstance(other, int):
            return self._type == int and self._value == other
        return False

    def __ne__(self, other: 'Element') -> bool:
        """
        Checks if two elements are not equal.

        :param other: Another element to compare.
        :type other: Element
        :return: True if elements have different values, False otherwise.
        :rtype: bool
        """
        return not self.__eq__(other)

    def __lt__(self, other: 'Element') -> bool:
        """
        Checks if this element is less than the other element.

        :param other: Another element to compare.
        :type other: Element
        :return: True if this element is less than the other element, False otherwise.
        :rtype: bool
        """
        assert self._type == other._type
        return self._value < other._value

    def __le__(self, other: 'Element') -> bool:
        """
        Checks if this element is less than or equal to the other element.

        :param other: Another element to compare.
        :type other: Element
        :return: True if this element is less than or equal to the other element, False otherwise.
        :rtype: bool
        """
        assert self._type == other._type
        return self._value <= other._value

    def __gt__(self, other: 'Element') -> bool:
        """
        Checks if this element is greater than the other element.

        :param other: Another element to compare.
        :type other: Element
        :return: True if this element is greater than the other element, False otherwise.
        :rtype: bool
        """
        assert self._type == other._type
        return self._value > other._value

    def __ge__(self, other: 'Element') -> bool:
        """
        Checks if this element is greater than or equal to the other element.

        :param other: Another element to compare.
        :type other: Element
        :return: True if this element is greater than or equal to the other element, False otherwise.
        :rtype: bool
        """
        assert self._type == other._type
        return self._value >= other._value

    def __hash__(self) -> int:
        """

        :return: The hash of the value of the element
        """
        return hash(self._value)

    def __str__(self) -> str:
        """
        Returns a string representation of the Element instance.

        :return: A string representation of the Element instance
        :rtype: str
        """
        if self._type is int:
            return f"{self._value}"
        return f"{self._value}"

    def __repr__(self) -> str:
        """
        Returns a string representation of the Element instance.

        :return: A string representation of the Element instance
        :rtype: str
        """
        return f"{self._value}"
