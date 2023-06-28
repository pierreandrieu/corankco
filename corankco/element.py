from typing import Union


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

    def __eq__(self, other) -> bool:
        """
        To compare two instances of Element

        :return: True iif they have same type and value
        :rtype: bool
        """
        if not isinstance(other, Element):
            return False
        return self._value == other._value

    def __ne__(self, other):
        """
        To compare if instance is different to another Element
        :return: True iif they have different type or different value
        :rtype: bool
        """
        return not self.__eq__(other)

    def __repr__(self) -> str:
        """
        Returns a string representation of the Element instance.

        :return: A string representation of the Element instance
        :rtype: str
        """

        return f"Element('{self._value}')"


