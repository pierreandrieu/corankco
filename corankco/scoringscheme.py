"""
Module to manage Scoring Schemes. The scoring schemes are two penalty vectors of 6 real values each. The details can be
found in the docstring of the ScoringScheme class
"""

from typing import List
from math import isnan


class InvalidScoringScheme(Exception):
    """
    Customized exception when the ScoringScheme is invalid because of the structure.
    """
    def __init__(self,
                 message="Scoring scheme must be 2 Lists. " +
                         "Each list must be a list of 6 real >= 0 values. " +
                         "For instance, [[0., 1., 1., 0., 0., 0.], [1., 1., 0., 1., 1., 0.]]"):
        self.message = message
        super().__init__(self.message)


class NonRealPositiveValuesScoringScheme(Exception):
    """
    Customized exception when the ScoringScheme is invalid because of a value found, not real positive.
    """
    def __init__(self, message="Each list must be a list of 6 real >= 0 values. "
                               "For instance, [[0., 1., 1., 0., 0., 0.], [1., 1., 0., 1., 1., 0.]]"):
        self.message = message
        super().__init__(self.message)


class ForbiddenAssociationPenaltiesScoringScheme(Exception):
    """
    Customized exception when the ScoringScheme is invalid because wring association of penalties.
    """
    def __init__(self,
                 message="The first value of the first List must be 0. "
                         "The second value of the first List must be > 0"
                         "The fourth value of the first List must be <= the fifth value of the second List"
                         "The first and second values of the second List must be equal. "
                         "The fourth and the fifth values of the second List must be equal"
                         "The third value of the second List must be > 0"
                         "For instance, [[0., 1., 1., 0., 0., 0.], [1., 1., 0., 1., 1., 0.]]"):
        self.message = message
        super().__init__(self.message)


class ScoringScheme:
    """

    The ScoringScheme class represents a scoring scheme for comparing rankings.

    :param penalties: A list of 2 penalty vectors i.e. two lists of size 6.
                      Let B be the first penalty vector and T be the second one, c be a consensus ranking (complete) and
                      r be a ranking. B: costs to pay for each elements x,y such that x < y in the consensus, more
                      precisely: B[0] if x < y in r, B[1] if x > y in r, B[2] if x is tied with y in r, B[3] if x is
                      ranked and y is not, B[4] if y is ranked and x is not, B[5] if x and y are non-ranked.
                      T: costs to pay for each elements x,y such that x is tied with y in the consensus, more precisely:
                      T[0] if x < y in r, T[1] if x > y in r, T[2] if x is tied with y in r, T[3] if x is ranked and y
                      is not, T[4] if y is ranked and x is not, T[5] if x and y are non-ranked

    :raises InvalidScoringScheme: If penalties is not of a correct format.
    :raises NonRealPositiveValuesScoringScheme: If one penalty is not a real value>= 0.
    :raises ForbiddenAssociationPenaltiesScoringScheme: If one of the following is not respected:
            - first value of first list must be 0
            - second value of the first List must be > 0
            - fourth value of the first List must be <= the fifth value of the second List
            - third value of second list must be > 0
            - first and second values of the second List must be equal
            - fourth and fifth values of the second List must be equal

    """

    def __init__(self, penalties: List[List[float]]):
        """

        Initialize the ScoringScheme object.

        :param penalties: A list of penalty vectors
        :rtype: List
        :raises InvalidScoringScheme: If penalties is not of a correct format.

        """
        # check types and lengths
        if not isinstance(penalties, list) or len(penalties) != 2:
            raise InvalidScoringScheme()
        if not isinstance(penalties[0], list) or not isinstance(penalties[1], list):
            raise InvalidScoringScheme()
        if len(penalties[0]) != 6 or len(penalties[1]) != 6:
            raise InvalidScoringScheme()

        # copy the penalties in a new List of List of floats
        penalties_copy: List[List[float]] = [[], []]
        for pen in penalties[0]:
            if (not isinstance(pen, float) and not isinstance(pen, int)) or pen < 0:
                raise NonRealPositiveValuesScoringScheme()
            penalties_copy[0].append(float(pen))
        for pen in penalties[1]:
            if (not isinstance(pen, float) and not isinstance(pen, int)) or pen < 0:
                raise NonRealPositiveValuesScoringScheme()
            penalties_copy[1].append(float(pen))

        # check assertions
        if penalties_copy[1][0] != penalties_copy[1][1] or penalties_copy[1][3] != penalties_copy[1][4] \
                or penalties_copy[0][3] > penalties_copy[0][4]:
            raise ForbiddenAssociationPenaltiesScoringScheme()
        if penalties_copy[0][0] > 0 or penalties_copy[1][2] > 0:
            raise ForbiddenAssociationPenaltiesScoringScheme()
        if penalties_copy[0][3] > penalties_copy[0][4]:
            raise ForbiddenAssociationPenaltiesScoringScheme()
        if penalties_copy[0][1] == 0:
            raise ForbiddenAssociationPenaltiesScoringScheme()
        self._penalty_vectors = penalties_copy

    @property
    def penalty_vectors(self) -> List[List[float]]:
        """
        Returns the List of two penalty vectors (each one is a List of 6 floats) of the ScoringScheme

        :return: List of two penalty vectors (each one is a List of 6 floats) of the ScoringScheme.
                 For instance, [[0., 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]]
        :rtype: List[List[float]]
        """
        return self._penalty_vectors

    @property
    def b_vector(self) -> List[float]:
        """
        Returns the List of 6 floats that corresponds to vector B according to Andrieu et al., IJAR 2022
        :return: vector B of the Scoring Scheme as a List of 6 floats.
        :rtype: List[float]
        """
        return self.penalty_vectors[0]

    @property
    def t_vector(self) -> List[float]:
        """
        Returns the List of 6 floats that corresponds to vector T according to Andrieu et al., IJAR 2022
        :return: penalty vector T of the Scoring Scheme as a List of 6 floats.
        :rtype: List[float]
        """
        return self.penalty_vectors[1]

    def __str__(self) -> str:
        """
        Returns a string view of the ScoringScheme
        :return: a string view of the ScoringScheme
        :rtype: str
        """
        return str(self._penalty_vectors)

    def __repr__(self) -> str:
        """
        Returns a string view of the ScoringScheme
        :return: a string view of the ScoringScheme
        :rtype: str
        """
        return str(self._penalty_vectors)

    def __mul__(self, other: float) -> 'ScoringScheme':
        """
        Defines the behavior of multiplying a ScoringScheme by a float.
        Multiplies all penalties in the ScoringScheme by the given integer.

        :param other: An integer to multiply the ScoringScheme by.
        :type other: int
        :return: A new ScoringScheme with all penalties multiplied by 'other'.
        :rtype: ScoringScheme
        """
        if not isinstance(other, float) and not isinstance(other, int):
            raise ValueError("Can only multiply by an integer or a float number")
        new_penalties: List[List[float]] = [[pen * float(other) for pen in penalty_vector]
                                            for penalty_vector in self._penalty_vectors]
        return ScoringScheme(new_penalties)

    def __rmul__(self, other: float) -> 'ScoringScheme':
        """
        Defines the behavior of multiplying a float by a ScoringScheme.
        Calls the __mul__ function to handle the operation.

        :param other: An integer to multiply the ScoringScheme by.
        :type other: int
        :return: A new ScoringScheme with all penalties multiplied by 'other'.
        :rtype: ScoringScheme
        """
        return self.__mul__(other)

    def description(self) -> str:
        """
        Returns a string that gives details on the ScoringScheme
        :return: a string that gives details on the ScoringScheme
        :rtype: str
        """
        desc = (
            "\nScoring scheme description\n"
            f"\tx before y in consensus\n"
            f"\t\tx before y in input ranking: {self.b_vector[0]}\n"
            f"\t\ty before x in input ranking: {self.b_vector[1]}\n"
            f"\t\tx and y tied in input ranking: {self.b_vector[2]}\n"
            f"\t\tx present y missing in input ranking: {self.b_vector[3]}\n"
            f"\t\tx missing y present ranking: {self.b_vector[4]}\n"
            f"\t\tx and y missing in input ranking: {self.b_vector[5]}\n"
            f"\tx and y tied in consensus\n"
            f"\t\tx before y in input ranking: {self.t_vector[0]}\n"
            f"\t\ty before x in input ranking: {self.t_vector[1]}\n"
            f"\t\tx and y tied in input ranking: {self.t_vector[2]}\n"
            f"\t\tx present y missing in input ranking: {self.t_vector[3]}\n"
            f"\t\tx missing y present ranking: {self.t_vector[4]}\n"
            f"\t\tx and y missing in input ranking: {self.t_vector[5]}\n"
        )
        return desc

    @staticmethod
    def get_pseudodistance_scoring_scheme() -> 'ScoringScheme':
        """
        Get the pseudo-distance defined in:
        Brancotte, Bryan & Rance, Bastien & Denise, Alain & Cohen-Boulakia, Sarah. (2014). ConQuR-Bio: Consensus Ranking
        with Query Reformulation for Biological Data. 10.1007/978-3-319-08590-6_13. .

        :return: The ScoringScheme [[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]]
        """
        return ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)

    @staticmethod
    def get_unifying_scoring_scheme():
        """
        Get the ScoringScheme that imitates the unification process, that is
        the non-ranked elements can be virtually considered as tied at the last position or the ranking
        :return: The ScoringScheme [[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]]
        """
        return ScoringScheme.get_unifying_scoring_scheme_p(1.)

    @staticmethod
    def get_induced_measure_scoring_scheme():
        """
        Get the induced mesure scoring scheme defined in "Bryan Brancotte, Agrégation de classements avec égalités :
        algorithmes, guides à l'utilisateur et applications aux données biologiques. University of Paris-Sud, Orsay,
        France, 2015". This measure is a fusion between the measure to handle incomplete rankings defined in:
        C. Dwork, R. Kumar, M. Naor, and D. Sivakumar. 2001. Rank aggregation methods for the Web. In Proceedings of the
        10th international conference on World Wide Web (WWW '01),
        and the distance to handle ties proposed by R. Fagin, R. Kumar, M. Mahdian, D. Sivakumar, and Erik Vee. 2004.
        Comparing and aggregating rankings with ties. In Proceedings of the twenty-third ACM SIGMOD-SIGACT-SIGART
        symposium on Principles of database systems (PODS '04).
        :return: The ScoringScheme [[0., 1., 1., 0., 0., 0.], [1., 1., 0., 0., 0., 0.]]
        """
        return ScoringScheme.get_induced_measure_scoring_scheme_p(1.)

    @staticmethod
    def get_pseudodistance_scoring_scheme_p(p_cost: float):
        """
        Get the pseudo-distance scoring scheme defined in:
        Brancotte, Bryan & Rance, Bastien & Denise, Alain & Cohen-Boulakia, Sarah. (2014).
        ConQuR-Bio: Consensus Ranking with Query Reformulation for Biological Data. 10.1007/978-3-319-08590-6_13
        with reap parameter p = cost of creating / breaking ties
        :param p_cost: the cost to create / break ties
        :return: The ScoringScheme [[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]]
        """
        return ScoringScheme(penalties=[[0., 1., p_cost, 0., 1., 0.], [p_cost, p_cost, 0., p_cost, p_cost, 0.]])

    @staticmethod
    def get_unifying_scoring_scheme_p(p_cost: float):
        """
        Get the ScoringScheme that imitates the unification process, that is
        the non-ranked elements can be virtually considered as tied at the last position or the ranking
        :param p_cost: the cost to create / break ties
        :return: The ScoringScheme [[0., 1., p, 0., 1., p], [p, p, 0., p, p, 0.]]
        """
        return ScoringScheme(penalties=[[0., 1., p_cost, 0., 1., p_cost], [p_cost, p_cost, 0., p_cost, p_cost, 0.]])

    @staticmethod
    def get_induced_measure_scoring_scheme_p(p_cost: float):
        """
        Get the ScoringScheme that imitates the unification process, that is
        the non-ranked elements can be virtually considered as tied at the last position or the ranking
        :param p_cost: the cost to create / break ties
        :return: The ScoringScheme [[0., 1., p, 0., 1., p], [p, p, 0., p, p, 0.]]
        """
        return ScoringScheme(penalties=[[0., 1., p_cost, 0., 0., 0.], [p_cost, p_cost, 0., 0., 0., 0.]])

    @staticmethod
    def get_extended_measure_scoring_scheme():
        """
        Get the ScoringScheme defined in []
        :return: The ScoringScheme
        """
        return ScoringScheme(penalties=[[0., 1., 0., 0., 0., 0.], [1., 1., 0., 1., 1., 1.]])

    def is_equivalent_to(self, other) -> bool:
        """
        Check if the current scoring scheme is equivalent to the given scoring scheme.

        :param other: A ScoringScheme object.
        :return: True if the scoring schemes are equivalent, False otherwise.
        """
        return self.__is_equivalent_to_generic(other, 6)

    def is_equivalent_to_on_complete_rankings_only(self, other) -> bool:
        """
        Check if the current scoring scheme is equivalent to the given scoring scheme on complete rankings

        :param other: A ScoringScheme object.
        :return: True if the scoring schemes are equivalent, False otherwise.
        """
        return self.__is_equivalent_to_generic(other, 3)

    def __is_equivalent_to_generic(self, other: 'ScoringScheme', stop: int) -> bool:
        """
        Check if current scoring scheme is equivalent to the given scoring scheme considering only ranges 0...stop-1.

        :param other: A ScoringScheme object.
        :param stop: the range of each penalty score to compare
        :return: True if the scoring schemes are equivalent, False otherwise.
        """
        pen2: List[List[float]] = other.penalty_vectors
        pen1: List[List[float]] = self._penalty_vectors
        coefficient: float = float("nan")
        for i in range(stop):
            if pen1[0][i] == 0:
                if pen2[0][i] != 0:
                    return False
            else:
                if pen2[0][i] == 0:
                    return False
                if isnan(coefficient):
                    coefficient = pen1[0][i] / pen2[0][i]
                else:
                    if pen1[0][i] / pen2[0][i] != coefficient:
                        return False
        return True

    def get_nickname(self) -> str:
        """
        Get a nickname of the scoring scheme.

        :return: A string representing a nickname of the scoring scheme.
        """
        if self.is_equivalent_to(ScoringScheme.get_unifying_scoring_scheme_p(1.)):
            return "UKSP"
        if self.is_equivalent_to(ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)):
            return "GPDP"
        if self.is_equivalent_to(ScoringScheme.get_induced_measure_scoring_scheme_p(1.)):
            return "IGKS"
        if self.is_equivalent_to(ScoringScheme.get_extended_measure_scoring_scheme()):
            return "EKS"
        return str(self)

    def __getitem__(self, item: int) -> List[float]:
        return self._penalty_vectors[item]
