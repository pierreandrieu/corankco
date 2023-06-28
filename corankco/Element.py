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
        if isinstance(value, (int, str)):
            self._value = value
        else:
            raise TypeError("Value must be of type int or str")

    def __repr__(self) -> str:
        """
        Returns a string representation of the Element instance.

        :return: A string representation of the Element instance
        :rtype: str
        """
        return str(self._value)
