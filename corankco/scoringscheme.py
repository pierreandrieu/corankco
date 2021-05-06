from typing import List
from math import isnan


class InvalidScoringScheme(Exception):
    pass


class NotRelevantScoringScheme(Exception):
    pass


class ScoringScheme:

    def __init__(self, penalties=None):
        if penalties is None:
            self.__penalty_vectors = [[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]]
        else:
            if type(penalties) is not list or len(penalties) != 2 or len(penalties[0]) != 6 or len(penalties[1]) != 6:
                raise InvalidScoringScheme
            penalties_copy = [[], []]
            for pen in penalties[0]:
                penalties_copy[0].append(float(pen))
            for pen in penalties[1]:
                penalties_copy[1].append(float(pen))

            if penalties_copy[1][0] != penalties_copy[1][1] or penalties_copy[1][3] != penalties_copy[1][4]:
                raise NotRelevantScoringScheme
            self.__penalty_vectors = penalties_copy

    @property
    def penalty_vectors(self) -> List[List[float]]:
        return self.__penalty_vectors

    def __str__(self) -> str:
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
