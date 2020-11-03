import unittest

class TestStringMethods(unittest.TestCase):
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()


def square(x):
    """Return the square of x.

    >>> square(2)
    4

    >>> square(-2)
    4
    """

    return x * x


if __name__ == '__main__':
    import doctest
    doctest.testmod()


def func(x):
    return x + 1


def test_answer():
    assert func(3) == 4


# ################

import tkinter

import unittest
root = tkinter.Tk()

class WidgetTestCase(unittest.TestCase):
    def setUp(self):
        self.widget = tkinter.Widget(widgetName='The widget', master=root)

    def test_default_widget_size(self):
        self.assertEqual(self.widget.size(), (50,50),
                         'incorrect default size')

    def test_widget_resize(self):
        self.widget.size(100,150)
        self.assertEqual(self.widget.size(), (100,150),
                         'wrong size after resize')