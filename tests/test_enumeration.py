import random
import unittest
from unittest import mock

from dreamcoder.enumeration import multicoreEnumeration
from dreamcoder.frontier import Frontier
from dreamcoder.grammar import Grammar
from dreamcoder.task import Task
from dreamcoder.type import arrow, tint


class TestEnumerationMain(unittest.TestCase):

    def test_multicore_enumeration_no_tasks(self):
        grammar = Grammar.uniform([])
        tasks = []
        frontiers, best_search_time = multicoreEnumeration(grammar, tasks)
        self.assertEqual(frontiers, [])
        self.assertEqual(best_search_time, {})

    @mock.patch('dreamcoder.enumeration.subprocess')
    def test_multicore_enumeration_single_task(self, mock_subprocess):
        mock_process = mock.MagicMock()
        response = '{"add1": []}'.encode('utf-8')
        mock_process.communicate.return_value = (response, None)
        mock_subprocess.Popen.return_value = mock_process

        def add1():
            x = random.choice(range(10))
            return {"i": x, "o": x + 1}

        grammar = Grammar.uniform([])
        example = {
            "name": "add1",
            "data": [add1() for _ in range(5000)],
        }
        task = Task(
            example["name"],
            arrow(tint, tint),
            [((ex["i"],), ex["o"]) for ex in example["data"]],
        )
        tasks = [task]
        frontiers, best_search_time = multicoreEnumeration(
            grammar, tasks, maximumFrontier=1, enumerationTimeout=1)
        self.assertIsInstance(frontiers, list)
        self.assertEqual(len(frontiers), 1)
        actual_frontier = frontiers[0]
        expect_frontier = Frontier([], task)
        self.assertEqual(actual_frontier.entries, expect_frontier.entries)
        self.assertEqual(actual_frontier.task, expect_frontier.task)
        self.assertIsInstance(best_search_time, dict)
        self.assertEqual([t.name for t in best_search_time.keys()], ["add1"])


if __name__ == '__main__':
    unittest.main()
