import unittest
from corankco.scoringscheme import ScoringScheme, InvalidScoringScheme, ForbiddenAssociationPenaltiesScoringScheme, \
    NonRealPositiveValuesScoringScheme


class TestScoringScheme(unittest.TestCase):

    def test_custom_initialization(self):
        ss = ScoringScheme(penalties=[[0., 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])
        self.assertEqual(ss.penalty_vectors, [[0., 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])

    def test_mult(self):
        ss = ScoringScheme(penalties=[[0., 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])
        self.assertEqual(str(2. * ss), str([[0., 2., 1.,0., 2., 0.], [1., 1., 0., 1., 1., 0.]]))
        self.assertEqual(str(ss * 2.), str([[0., 2., 1., 0., 2., 0.], [1., 1., 0., 1., 1., 0.]]))
        self.assertEqual(str(ss * 2), str([[0., 2., 1., 0., 2., 0.], [1., 1., 0., 1., 1., 0.]]))

    def test_invalid_penalty_length(self):
        with self.assertRaises(InvalidScoringScheme):
            # length 5 and 6
            ScoringScheme(penalties=[[0., 1., 0.5, 0., 1.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])

    def test_invalid_assertion_penalties(self):
        with self.assertRaises(ForbiddenAssociationPenaltiesScoringScheme):
            # B[0] != 0
            ScoringScheme(penalties=[[0.5, 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])
        with self.assertRaises(ForbiddenAssociationPenaltiesScoringScheme):
            # T[2] != 0
            ScoringScheme(penalties=[[0, 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0.5, 0.5, 0.5, 0.]])
        with self.assertRaises(ForbiddenAssociationPenaltiesScoringScheme):
            # T[0] != T[1]
            ScoringScheme(penalties=[[0, 1., 0.5, 0., 1., 0.], [0.5, 1., 0., 0.5, 0.5, 0.]])
        with self.assertRaises(ForbiddenAssociationPenaltiesScoringScheme):
            # T[3] != T[4]
            ScoringScheme(penalties=[[0, 1., 0.5, 0., 1., 0.], [1., 1., 0., 1., 0.5, 0.]])
        with self.assertRaises(ForbiddenAssociationPenaltiesScoringScheme):
            # B[3] > B[4]
            ScoringScheme(penalties=[[0, 1., 0.5, 1.5, 1., 0.], [1., 1., 0., 1., 1., 0.]])

        with self.assertRaises(ForbiddenAssociationPenaltiesScoringScheme):
            # B[1] == 0
            ScoringScheme(penalties=[[0, 0., 0.5, 0.5, 1., 0.], [1., 1., 0., 1., 1., 0.]])

    def test_invalid_penalty_element_type(self):
        with self.assertRaises(NonRealPositiveValuesScoringScheme):
            # 'a' is not a number
            ScoringScheme(penalties=[[0., 1., 'a', 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])

    def test_invalid_penalty_type(self):
        with self.assertRaises(InvalidScoringScheme):
            # penalties is not a list
            ScoringScheme(penalties='invalid')

    def test_invalid_penalty_dimension(self):
        with self.assertRaises(InvalidScoringScheme):
            # Only one penalty vector, should be two
            ScoringScheme(penalties=[[0., 1., 0.5, 0., 1., 0.]])

    def test_negative_penalty_value(self):
        with self.assertRaises(NonRealPositiveValuesScoringScheme):
            # -0.5 is less than 0.
            ScoringScheme(penalties=[[0., 1., -0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])

    def test_properties(self):
        sc = ScoringScheme([[0., 1., 2., 3., 4., 5.], [6., 6., 0., 7., 7., 8.]])
        self.assertEqual(sc.b1, 0.)
        self.assertEqual(sc.b2, 1.)
        self.assertEqual(sc.b3, 2.)
        self.assertEqual(sc.b4, 3.)
        self.assertEqual(sc.b5, 4.)
        self.assertEqual(sc.b6, 5.)
        self.assertEqual(sc.t1_and_t2, 6.)
        self.assertEqual(sc.t3, 0.)
        self.assertEqual(sc.t4_and_t5, 7.)
        self.assertEqual(sc.t6, 8.)
        self.assertEqual(sc.b_vector, [0., 1., 2., 3., 4., 5.])
        self.assertEqual(sc.t_vector, [6., 6., 0., 7., 7., 8.])

    def test_pseudodistance_scoring_scheme(self):
        ss = ScoringScheme.get_pseudodistance_scoring_scheme()
        self.assertEqual(ss.penalty_vectors, [[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]])


if __name__ == '__main__':
    unittest.main()
