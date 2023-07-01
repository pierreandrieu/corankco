from typing import List, Set
from corankco.element import Element
from corankco.ranking import Ranking
import unittest


class TestRanking(unittest.TestCase):
    def setUp(self):
        self.ranking = Ranking.from_list([{'3', '2'}, {'1'}])

    def test_init(self):
        # Test with disjoint sets
        buckets: List[Set[Element]] = [{Element('A'), Element('B')}, {Element('C')}]
        ranking = Ranking(buckets)
        self.assertEqual(ranking._buckets, buckets)
        self.assertEqual(ranking.positions, {Element('A'): 1, Element('B'): 1, Element('C'): 3})

        # Test with overlapping sets
        buckets = [{Element('A'), Element('B')}, {Element('B'), Element('C')}]
        with self.assertRaises(ValueError):
            ranking = Ranking(buckets)
            if ranking:
                pass

    def test_str_init(self):
        # Test with disjoint sets
        buckets: List[Set[str]] = [{'A', 'B'}, {'C'}]
        ranking = Ranking.from_list(buckets)
        self.assertEqual(ranking._buckets, [{Element('A'), Element('B')}, {Element('C')}])
        self.assertEqual(ranking.positions, {Element('A'): 1, Element('B'): 1, Element('C'): 3})

        # Test with overlapping sets
        buckets = [{'A', 'B'}, {'B', 'C'}]
        with self.assertRaises(ValueError):
            ranking = Ranking.from_list(buckets)
            if ranking:
                pass

    def test_int_init(self):
        # Test with disjoint sets
        buckets: List[Set[int]] = [{1, 2}, {3}]
        ranking = Ranking.from_list(buckets)
        self.assertEqual(ranking._buckets, [{1, 2}, {3}])
        self.assertEqual(ranking.positions, {1: 1, 2: 1, 3: 3})

        # Test with overlapping sets
        buckets = [{1, 2}, {2, 3}]
        with self.assertRaises(ValueError):
            ranking = Ranking.from_list(buckets)
            if ranking:
                pass

    def test_positions(self):
        buckets: List[Set[Element]] = [{Element('A'), Element('B')}, {Element('C')}]
        ranking = Ranking(buckets)
        self.assertEqual(ranking.positions, {Element('A'): 1, Element('B'): 1, Element('C'): 3})

    def test_str(self):
        # Test with int elements
        buckets = [{Element(2), Element(3)}, {Element(1)}]
        ranking = Ranking(buckets)
        self.assertEqual(str(ranking), "[{2, 3}, {1}]")

        # Test with str elements
        buckets = [{Element('Bob')}]
        ranking = Ranking(buckets)
        self.assertEqual(str(ranking), "[{'Bob'}]")

    def test_iter(self):
        # Test for the __iter__ method
        self.assertEqual(list(self.ranking), [{'3', '2'}, {'1'}])

    def test_len(self):
        # Test for the __len__ method
        self.assertEqual(len(self.ranking), 2)

    def test_domain(self):
        # Test for the domain method
        self.assertEqual(sorted(list(self.ranking.domain)), sorted(list({'3', '2', '1'})))

    def test_nb_elements(self):
        # Test for the nb_elements method
        self.assertEqual(self.ranking.nb_elements, 3)

    def test_ranking_getitem(self):
        bucket1 = {1, 2, 3}
        bucket2 = {4, 5, 6}
        bucket3 = {7, 8, 9}
        ranking = Ranking.from_list([bucket1, bucket2, bucket3])
        assert ranking[0] == bucket1
        assert ranking[1] == bucket2
        assert ranking[2] == bucket3


# To run the tests:
if __name__ == '__main__':
    unittest.main()
