from typing import Union, Type


class Element:
    """
    A class to represent an element of a ranking.

    :param value: the value of the element, either an integer or a string
    :type value: Union[int, str]
    """

    def __init__(self, value: Union[int, str]):
        """
        Constructs an Element instance with the given value.

        :param value: The value of the element, either an integer or a string
        :type value: Union[int, str]
        :raises TypeError: If value is not an integer or a string
        """
        if isinstance(value, int):
            self._type = int
        elif isinstance(value, str):
            self._type = str
        else:
            raise ValueError("Value must be int or str")
        self._value = value

    def _get_value(self) -> Union[int, str]:
        """
        returns the value of the instance
        :return: value of the instance
        :rtype: Union[int, str]
        """
        return self._value

    def _get_type(self) -> Type:
        """
        returns the type of the instance
        :return: type of the instance
        :rtype: Type
        """
        return self._type

    value = property(_get_value)
    type = property(_get_type)

    def __eq__(self, other: 'Element') -> bool:
        """
        Checks if two elements are equal.

        :param other: Another element to compare.
        :type other: Element
        :return: True if both elements have the same value, False otherwise.
        :rtype: bool
        """
        if not isinstance(other, Element):
            return False
        return self._value == other._value

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
        assert(self._type == other._type)
        return self._value < other._value

    def __le__(self, other: 'Element') -> bool:
        """
        Checks if this element is less than or equal to the other element.

        :param other: Another element to compare.
        :type other: Element
        :return: True if this element is less than or equal to the other element, False otherwise.
        :rtype: bool
        """
        assert(self._type == other._type)
        return self._value <= other._value

    def __gt__(self, other: 'Element') -> bool:
        """
        Checks if this element is greater than the other element.

        :param other: Another element to compare.
        :type other: Element
        :return: True if this element is greater than the other element, False otherwise.
        :rtype: bool
        """
        assert(self._type == other._type)
        return self._value > other._value

    def __ge__(self, other: 'Element') -> bool:
        """
        Checks if this element is greater than or equal to the other element.

        :param other: Another element to compare.
        :type other: Element
        :return: True if this element is greater than or equal to the other element, False otherwise.
        :rtype: bool
        """
        assert(self._type == other._type)
        return self._value >= other._value

    def __repr__(self) -> str:
        """
        Returns a string representation of the Element instance.

        :return: A string representation of the Element instance
        :rtype: str
        """
        if self._type is int:
            return f"Element({self._value})"
        else:
            return f"Element('{self._value}')"

