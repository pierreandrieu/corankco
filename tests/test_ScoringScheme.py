import unittest
from numpy import array
from corankco.scoringscheme import ScoringScheme, InvalidScoringScheme


class TestScoringScheme(unittest.TestCase):
    def test_default_initialization(self):
        ss = ScoringScheme()
        self.assertEqual(ss.penalty_vectors, [[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]])

    def test_custom_initialization(self):
        ss = ScoringScheme(penalties=[[0., 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])
        self.assertEqual(ss.penalty_vectors, [[0., 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])

    def test_initialization_with_numpy_array(self):
        penalties = array([[0., 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])
        ss = ScoringScheme(penalties=penalties)
        self.assertEqual(ss.penalty_vectors, [[0., 1., 0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])

    def test_invalid_penalty_length(self):
        with self.assertRaises(InvalidScoringScheme):
            # length 5 and 6
            ScoringScheme(penalties=[[0., 1., 0.5, 0., 1.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])

    def test_invalid_penalty_element_type(self):
        with self.assertRaises(InvalidScoringScheme):
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

    def test_invalid_penalty_value(self):
        with self.assertRaises(InvalidScoringScheme):
            # 2. is greater than 1.
            ScoringScheme(penalties=[[0., 1., 2., 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])

    def test_negative_penalty_value(self):
        with self.assertRaises(InvalidScoringScheme):
            # -0.5 is less than 0.
            ScoringScheme(penalties=[[0., 1., -0.5, 0., 1., 0.], [0.5, 0.5, 0., 0.5, 0.5, 0.]])

    def test_b1_property(self):
        ss = ScoringScheme()
        self.assertEqual(ss.b1, 0.)

    def test_b2_property(self):
        ss = ScoringScheme()
        self.assertEqual(ss.b2, 1.)

    def test_pseudodistance_scoring_scheme(self):
        ss = ScoringScheme.get_pseudodistance_scoring_scheme()
        self.assertEqual(ss.penalty_vectors, [[0., 1., 1., 0., 1., 0.], [1., 1., 0., 1., 1., 0.]])


if __name__ == '__main__':
    unittest.main()
