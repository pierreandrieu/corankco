class InvalidScoringScheme(Exception):
    pass


class NotRelevantScoringScheme(Exception):
    pass


class ScoringScheme:

    def __init__(self, penalties=None):
        if penalties is None:
            self._penalties = [[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]]
        else:
            if type(penalties) is not list or len(penalties) != 2 or len(penalties[0]) != 6 or len(penalties[1]) != 6:
                raise InvalidScoringScheme
            if penalties[1][0] != penalties[1][1] or penalties[1][3] != penalties[1][4]:
                raise NotRelevantScoringScheme
            self._penalties = penalties

    @property
    def penalty_vectors_str(self):
        return self._penalties

    def __str__(self):
        return str(self._penalties)

    def description(self):
        # return str(self._penalties)
        return "\nScoring scheme description\n\tx before y in consensus\n\t\tx before y in input ranking: "\
               + str(self._penalties[0][0])\
               + "\n\t\ty before x in input ranking: "+str(self._penalties[0][1])\
               + "\n\t\tx and y tied in input ranking: " + str(self._penalties[0][2])\
               + "\n\t\tx present y missing in input ranking: " + str(self._penalties[0][3])\
               + "\n\t\tx missing y present ranking: " + str(self._penalties[0][4]) \
               + "\n\t\tx and y missing in input ranking: " + str(self._penalties[0][4]) \
               + "\n\tx and y tied in consensus\n\t\tx before y in input ranking: " + str(self._penalties[1][0]) \
                + "\n\t\ty before x in input ranking: " + str(self._penalties[1][1]) \
                + "\n\t\tx and y tied in input ranking: " + str(self._penalties[1][2]) \
                + "\n\t\tx present y missing in input ranking: " + str(self._penalties[1][3]) \
                + "\n\t\tx missing y present ranking: " + str(self._penalties[1][4]) \
                + "\n\t\tx and y missing in input ranking: " + str(self._penalties[1][4])

    @staticmethod
    def get_pseudodistance_scoring_scheme():
        return ScoringScheme(penalties=[[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]])

    @staticmethod
    def get_unifying_scoring_scheme():
        return ScoringScheme(penalties=[[0., 1., 1., 0., 1., 1.], [1., 1., 0., 1., 1., 0.]])

    @staticmethod
    def get_induced_measure_scoring_scheme():
        return ScoringScheme(penalties=[[0., 1., 1., 0., 0., 0.], [1., 1., 0., 0., 0., 0.]])
