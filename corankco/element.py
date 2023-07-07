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
            raise TypeError("Value must be int or str, ", type(value), " found")
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

    def can_be_int(self):
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
        elif isinstance(other, str):
            return self.type == str and self.value == other
        elif isinstance(other, int):
            return self._type == int and self._value == other
        else:
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

    def __hash__(self):
        return hash(self._value)

    def __str__(self) -> str:
        """
        Returns a string representation of the Element instance.

        :return: A string representation of the Element instance
        :rtype: str
        """
        if self._type is int:
            return f"{self._value}"
        else:
            return f"{self._value}"

    def __repr__(self) -> str:
        """
        Returns a string representation of the Element instance.

        :return: A string representation of the Element instance
        :rtype: str
        """
        return f"{self._value}"


class PairwiseElementComparison:
    """
    Class to encapsulate the cost of the different relative orders for two elements in a consensus ranking within a
    Kemeny prism
    """
    def __init__(self, x: Element, y: Element, x_before_y: float, x_after_y: float, x_tied_y: float):
        if x <= y:
            self._x: Element = x
            self._y: Element = y
            self._x_before_y: float = x_before_y
            self._x_after_y: float = x_after_y
            self._x_tied_y: float = x_tied_y
        else:
            self._x: Element = y
            self._y: Element = x
            self._x_before_y: float = x_after_y
            self._x_after_y: float = x_before_y
            self._x_tied_y: float = x_tied_y

    @property
    def x(self) -> Element:
        """
        Property to get the x element
        :return: x
        """
        return self._x

    @property
    def y(self) -> Element:
        """
        Property to get the y element
        :return: y
        """
        return self._y

    @property
    def x_before_y(self) -> float:
        """
        Property to get the cost to place x before y in a consensus in a Kemeny prism
        :return: cost to place x before y in the consensus in a Kemeny prism
        """
        return self._x_before_y

    @property
    def x_after_y(self) -> float:
        """
        Property to get the cost to place x after y in a consensus in a Kemeny prism
        :return: cost to place x after y in a consensus in a Kemeny prism
        """
        return self._x_after_y

    @property
    def x_tied_y(self) -> float:
        """
        Property to get the cost to tie x and y in a consensus in a Kemeny prism
        :return: cost to tie x and y in a consensus in a Kemeny prism
        """
        return self._x_tied_y

    def x_before_y_is_minimal(self) -> bool:
        return self.x_before_y <= self.x_after_y and self.x_before_y <= self._x_tied_y

    def y_before_x_is_minimal(self) -> bool:
        return self.x_after_y <= self.x_before_y and self.x_after_y <= self.x_tied_y

    def x_tied_y_is_minimal(self) -> bool:
        return self.x_tied_y <= self.x_before_y and self.x_tied_y <= self.x_after_y

    def __hash__(self):
        return hash((self._x, self._y))

