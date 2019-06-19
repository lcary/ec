import unittest

from eclib.enumeration import multicoreEnumeration
from eclib.grammar import Grammar


class TestEnumerationMain(unittest.TestCase):

    def test_multicore_enumeration(self):
        grammar = Grammar.uniform([])
        tasks = []
        frontiers, best_search_time = multicoreEnumeration(grammar, tasks)
        self.assertEqual(frontiers, [])
        self.assertEqual(best_search_time, {})


if __name__ == '__main__':
    unittest.main()
