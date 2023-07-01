import unittest
from corankco.element import Element


class TestElement(unittest.TestCase):

    def test_creation_from_str(self):
        elem = Element("A")
        self.assertEqual(elem._value, 'A')

    def test_creation_from_int(self):
        elem = Element(1)
        self.assertEqual(elem._value, 1)

    def test_invalid_type(self):
        with self.assertRaises(TypeError):
            Element(1.0)

    def test_equal(self):
        elem1 = Element(1)
        elem2 = Element(1)
        self.assertEqual(elem1, elem2)

    def test_not_equal(self):
        elem1 = Element(1)
        elem2 = Element(2)
        self.assertNotEqual(elem1, elem2)

    def test_str(self):
        elem = Element("A")
        self.assertEqual(str(elem), "A")
        elem = Element(1)
        self.assertEqual(str(elem), "1")

    def test_repr(self):
        elem = Element("A")
        self.assertEqual(repr(elem), 'A')

    def test_type(self):
        elem1 = Element(1)
        self.assertEqual(elem1.type, int)
        elem2 = Element('A')
        self.assertEqual(elem2.type, str)

    def test_assertion(self):
        elem_int = Element(1)
        elem_str = Element('A')
        with self.assertRaises(AssertionError):
            if elem_int < elem_str:
                pass
        with self.assertRaises(AssertionError):
            if elem_int > elem_str:
                pass
        with self.assertRaises(AssertionError):
            if elem_int <= elem_str:
                pass
        with self.assertRaises(AssertionError):
            if elem_int >= elem_str:
                pass

    def test_comparison(self):
        elem1 = Element(1)
        elem2 = Element(2)
        self.assertTrue(elem1 < elem2)
        self.assertTrue(elem1 <= elem2)
        self.assertFalse(elem1 > elem2)
        self.assertFalse(elem1 >= elem2)
        self.assertFalse(elem1 == elem2)
        self.assertTrue(elem1 != elem2)

        elem1 = Element('A')
        elem2 = Element('B')
        self.assertTrue(elem1 < elem2)
        self.assertTrue(elem1 <= elem2)
        self.assertFalse(elem1 > elem2)
        self.assertFalse(elem1 >= elem2)
        self.assertFalse(elem1 == elem2)
        self.assertTrue(elem1 != elem2)

    def test_can_be_int(self):
        elem1 = Element('A')
        elem2 = Element('1')
        elem3 = Element(1)
        self.assertFalse(elem1.can_be_int())
        self.assertTrue(elem2.can_be_int())
        self.assertTrue(elem3.can_be_int())


if __name__ == '__main__':
    unittest.main()
