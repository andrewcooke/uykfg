from logging import DEBUG, basicConfig
from unittest import TestCase
from uykfg.nest.finder import possible_names


class NamesTest(TestCase):

    def assert_names(self, artist, *names):
        results = list(possible_names(artist))
        assert len(results) == len(names), results
        assert set(results) == set(names), results

    def test_names(self):
        basicConfig(level=DEBUG)
        self.assert_names('bob', 'bob')
        self.assert_names('Xela & Jefre Cantu-Ledesma',
            'Xela & Jefre Cantu-Ledesma', 'Xela', 'Jefre Cantu-Ledesma')
        self.assert_names('the foo band',
            'the foo band', 'foo')
        self.assert_names('the foo & bar band',
            'the foo & bar band', 'foo & bar', 'foo', 'bar', 'the foo', 'bar band')
        self.assert_names('bar & the foo band',
            'bar & the foo band', 'foo', 'bar', 'the foo band', 'bar & the foo', 'the foo')
        self.assert_names('foo, bar, baz',
            'foo, bar, baz', 'foo', 'bar', 'baz')
