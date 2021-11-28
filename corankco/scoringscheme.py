from typing import List
from math import isnan
from numpy import ndarray


class InvalidScoringScheme(Exception):
    pass


class NotRelevantScoringScheme(Exception):
    pass


class ScoringScheme:

    def __init__(self, penalties=None):
        if penalties is None:
            self.__penalty_vectors = [[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]]
        else:
            if type(penalties) is not list and type(penalties) is not tuple and type(penalties) is not ndarray:
                print(type(penalties))
                raise InvalidScoringScheme
            elif len(penalties) != 2:
                raise InvalidScoringScheme
            elif type(penalties[0]) is not list and type(penalties[0]) is not tuple and type(penalties[0]) is not ndarray:
                raise InvalidScoringScheme
            elif type(penalties[1]) is not list and type(penalties[1]) is not tuple and type(penalties[1]) is not ndarray:
                raise InvalidScoringScheme
            elif len(penalties[0]) != 6 or len(penalties[1]) != 6:
                raise InvalidScoringScheme
            penalties_copy = [[], []]
            for pen in penalties[0]:
                if float(pen) < 0:
                    raise InvalidScoringScheme("Coefficients must be >= 0")

                penalties_copy[0].append(float(pen))
            for pen in penalties[1]:
                penalties_copy[1].append(float(pen))
                if float(pen) < 0:
                    raise InvalidScoringScheme("Coefficients must be >= 0")
            if penalties_copy[1][0] != penalties_copy[1][1] or penalties_copy[1][3] != penalties_copy[1][4]:
                raise NotRelevantScoringScheme("Must have T1 = T2 and T4 = T5")
            if penalties_copy[0][0] > 0 or penalties_copy[1][2] > 0:
                raise NotRelevantScoringScheme("Must have B[1] = 0")
            self.__penalty_vectors = penalties_copy

    def __get_b1(self) -> float:
        return self.__penalty_vectors[0][0]

    def __get_b2(self) -> float:
        return self.__penalty_vectors[0][1]

    def __get_b3(self) -> float:
        return self.__penalty_vectors[0][2]

    def __get_b4(self) -> float:
        return self.__penalty_vectors[0][3]

    def __get_b5(self) -> float:
        return self.__penalty_vectors[0][4]

    def __get_b6(self) -> float:
        return self.__penalty_vectors[0][5]

    def __get_t1_and_t2(self) -> float:
        return self.__penalty_vectors[1][0]

    def __get_t3(self) -> float:
        return self.__penalty_vectors[1][2]

    def __get_t4_and_t5(self) -> float:
        return self.__penalty_vectors[1][3]

    def __get_t6(self) -> float:
        return self.__penalty_vectors[1][5]

    b1 = property(__get_b1)
    b2 = property(__get_b2)
    b3 = property(__get_b3)
    b4 = property(__get_b4)
    b5 = property(__get_b5)
    b6 = property(__get_b6)
    t1_t2 = property(__get_t1_and_t2)
    t3 = property(__get_t3)
    t4_t5 = property(__get_t4_and_t5)
    t6 = property(__get_t6)

    @property
    def penalty_vectors(self) -> List[List[float]]:
        return self.__penalty_vectors

    def __str__(self) -> str:
        return str(self.__penalty_vectors)

    def __repr__(self) -> str:
        return str(self.__penalty_vectors)

    def description(self):
        return "\nScoring scheme description\n\tx before y in consensus\n\t\tx before y in input ranking: "\
               + str(self.__penalty_vectors[0][0])\
               + "\n\t\ty before x in input ranking: "+str(self.__penalty_vectors[0][1])\
               + "\n\t\tx and y tied in input ranking: " + str(self.__penalty_vectors[0][2])\
               + "\n\t\tx present y missing in input ranking: " + str(self.__penalty_vectors[0][3])\
               + "\n\t\tx missing y present ranking: " + str(self.__penalty_vectors[0][4]) \
               + "\n\t\tx and y missing in input ranking: " + str(self.__penalty_vectors[0][5]) \
               + "\n\tx and y tied in consensus\n\t\tx before y in input ranking: " + str(self.__penalty_vectors[1][0]) \
                + "\n\t\ty before x in input ranking: " + str(self.__penalty_vectors[1][1]) \
                + "\n\t\tx and y tied in input ranking: " + str(self.__penalty_vectors[1][2]) \
                + "\n\t\tx present y missing in input ranking: " + str(self.__penalty_vectors[1][3]) \
                + "\n\t\tx missing y present ranking: " + str(self.__penalty_vectors[1][4]) \
                + "\n\t\tx and y missing in input ranking: " + str(self.__penalty_vectors[1][5])

    @staticmethod
    def get_pseudodistance_scoring_scheme():
        return ScoringScheme.get_pseudodistance_scoring_scheme_p(1.)

    @staticmethod
    def get_unifying_scoring_scheme():
        return ScoringScheme.get_unifying_scoring_scheme_p(1.)

    @staticmethod
    def get_induced_measure_scoring_scheme():
        return ScoringScheme.get_induced_measure_scoring_scheme_p(1.)

    @staticmethod
    def get_pseudodistance_scoring_scheme_p(p: float):
        return ScoringScheme(penalties=[[0., 1., p, 0., 1., 0.], [p, p, 0., p, p, 0.]])

    @staticmethod
    def get_unifying_scoring_scheme_p(p: float):
        return ScoringScheme(penalties=[[0., 1., p, 0., 1., p], [p, p, 0., p, p, 0.]])

    @staticmethod
    def get_induced_measure_scoring_scheme_p(p: float):
        return ScoringScheme(penalties=[[0., 1., p, 0., 0., 0.], [p, p, 0., 0., 0., 0.]])

    @staticmethod
    def get_extended_measure_scoring_scheme():
        return ScoringScheme(penalties=[[0., 1., 0., 0., 0., 0.], [1., 1., 0., 1., 1., 1.]])

    @staticmethod
    def get_fagin_score_for_complete_ranking(p: float):
        return ScoringScheme(penalties=[[0., 1., p, 0., 0., 0.], [p, p, 0., 0., 0., 0.]])

    def is_equivalent_to(self, sc2: List[List[float or int]]) -> bool:
        return self.__is_equivalent_to_generic(sc2, 6)

    def is_equivalent_to_on_complete_rankings_only(self, sc2: List[List[float or int]]) -> bool:
        return self.__is_equivalent_to_generic(sc2, 3)

    def __is_equivalent_to_generic(self, sc2: List[List[float or int]], stop: int) -> bool:
        second_scoring_scheme = ScoringScheme(sc2)
        pen2 = second_scoring_scheme.__penalty_vectors
        pen1 = self.__penalty_vectors
        coefficient = float("nan")
        for i in range(stop):
            if pen1[0][i] == 0:
                if pen2[0][i] != 0:
                    return False
            else:
                if pen2[0][i] == 0:
                    return False
                else:
                    if isnan(coefficient):
                        coefficient = pen1[0][i] / pen2[0][i]
                    else:
                        if pen1[0][i] / pen2[0][i] != coefficient:
                            return False
        return True
