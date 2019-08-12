"""
This module includes more list tasks from the following master list:
https://docs.google.com/document/d/1D99neDlUYXm1v4-5pQVsjh8V2mWKHTCArQ7Q9u9ea8Q/edit
"""
from abc import ABC, abstractmethod
from functools import reduce
import json
import os
import random
from collections import Counter, OrderedDict

from dreamcoder.utilities import get_data_dir

JSON_FILE = os.path.join(get_data_dir(), "more_list_tasks.json")

Integer = 'int'
ListOfInts = 'list-of-int'
Boolean = 'bool'


class SkipExample(Exception):
    """ Raise to skip an example for a given input. """


class TaskGenerator(ABC):
    """
    A TaskGenerator must have the following class attributes:
      - name
      - input_type
      - output_type

    A TaskGenerator must also implement the following functions:
      - func(inputs)
      - make_examples()

    Example task:

        MyTaskGenerator(TaskGenerator):
            name = None
            input_type = None
            output_type = None

            def func(self, x):
                x0 = x[0]
                return [x0 for _ in range(x0)]

            def make_examples(self):
                ...

    Example task format:

        [{
            "type": {"input": "list-of-int", "output": "list-of-int"},
            "name": "add-k with k=0",
            "examples": [
                {"i": [], "o": []},
                {"i": [1, 7, 1, 10, 1], "o": [1, 7, 1, 10, 1]},
                {"i": [2, 14], "o": [2, 14]}
        ]}

    """
    name = None
    input_type = None
    output_type = None

    def __init__(self):
        assert self.name is not None
        assert self.input_type is not None
        assert self.output_type is not None
        self.examples = self.make_examples()
        self.run_unit_tests()

    @abstractmethod
    def func(self, inputs):
        """
        Function to be applied to inputs, generating outputs.
        """
        pass

    @abstractmethod
    def make_examples(self):
        pass

    def example(self, inputs):
        return {'i': inputs, 'o': self.func(inputs)}

    @staticmethod
    def _to_json(name, input_type, output_type, examples):
        return {
            'name': name,
            'type': {'input': input_type, 'output': output_type},
            'examples': examples
        }

    def json(self):
        return self._to_json(self.name, self.input_type, self.output_type, self.examples)

    @property
    def unit_tests(self):
        """
        Sample input-output pairs for function verification.

        Note that actual input-output example pairs are generated, these are just for
        verifying that the function works properly.
        """
        return []

    def run_unit_tests(self):
        """
        Verify that the function works properly on some sample input-output pairs.
        """
        for i, o in self.unit_tests:
            try:
                assert self.func(i) == o
            except AssertionError as e:
                msg = (
                    'ERROR: Unable to verify that sample inputs ({}) '
                    'evaluate to outputs ({}) for task ({})')
                print(msg.format(i, o, self.name))
                print('DEBUG: actual outputs: {}'.format(self.func(i)))
                raise e
            except Exception as e:
                msg = (
                    'ERROR: Unable to run task ({}) function for sample inputs ({}) '
                    'evaluate to outputs ({})')
                print(msg.format(self.name, i, o))
                raise e


class ShuffledRangeTask(TaskGenerator, ABC):
    """
    A ShuffledRangeTask has the following optional knobs as class attributes:
      - num_examples (int): number of examples to create
    """
    num_examples = 20

    def make_examples(self):
        examples = [self.example([n]) for n in range(self.num_examples)]
        random.shuffle(examples)
        return examples


class RandomListTask(TaskGenerator, ABC):
    """
    A RandomListTask has the following optional knobs as class attributes:
      - min_val (int): minimum value in random list created
      - max_val (int): maximum value in random list created
      - min_len (int): minimum length of random list created
      - max_len (int): maximum length of random list created
      - num_examples (int): number of random lists to create
    """
    min_val = 0
    max_val = 99
    min_len = 0
    max_len = 10
    num_examples = 20

    def random_list(self):
        list_range = range(random.randint(self.min_len, max(self.min_len, self.max_len)))
        return [random.randint(self.min_val, self.max_val) for _ in list_range]

    def make_examples(self):
        created = 0
        examples = []
        while created < self.num_examples:
            i = self.random_list()
            try:
                o = self.example(i)
            except SkipExample:
                continue
            except Exception as e:
                print('ERROR: unable to generate outputs for task ({}) and inputs ({})'.format(
                    self.name, i))
                raise e
            else:
                examples.append(o)
                created += 1
        return examples


class Length(RandomListTask):
    """
    Length of list.
    """
    name = 'length'
    input_type = ListOfInts
    output_type = Integer

    def func(self, x):
        return len(x)

    @property
    def unit_tests(self):
        return [
            ([3, 9, 3, 8, 2, 7], 6),
            ([8, 8, 1, 3], 4),
            ([7, 3, 1, 4, 4, 1, 1, 9, 7, 1, 7, 1], 12),
        ]


class IsEmpty(RandomListTask):
    name = 'is_empty'
    input_type = ListOfInts
    output_type = Boolean

    def func(self, x):
        return not bool(x)

    @property
    def unit_tests(self):
        return [
            ([], True),
            ([1], False),
            ([0], False),
            ([2, 1, 7, 1, 8], False),
        ]


class Max(RandomListTask):
    name = 'max'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        if not x:
            return []
        return [max(x)]

    @property
    def unit_tests(self):
        return [
            ([], []),
            ([3, 9, 3, 8, 2, 7], [9]),
            ([8, 8, 1, 3], [8]),
            ([2, 7, 9, 1], [9]),
            ([7, 3, 1, 4, 4, 1, 1, 9, 7, 1, 7, 1], [9]),
            ([6, 3, 1, 6, 2, 7], [7]),
            ([4, 6, 5, 2, 2, 3, 5], [6]),
        ]


class Min(RandomListTask):
    name = 'min'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        if not x:
            return []
        return [min(x)]

    @property
    def unit_tests(self):
        return [
            ([], []),
            ([3, 9, 3, 8, 2, 7], [2]),
            ([8, 8, 1, 3], [1]),
            ([2, 7, 9, 1], [1]),
            ([7, 3, 1, 4, 4, 1, 1, 9, 7, 1, 7, 1], [1]),
            ([6, 3, 1, 6, 2, 7], [1]),
            ([4, 6, 5, 2, 2, 3, 5], [2]),
        ]


class Reverse(RandomListTask):
    """
    Reverse the list.
    """
    name = 'reverse'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return list(reversed(x))

    @property
    def unit_tests(self):
        return [
            ([3, 9, 2, 1, 8, 8], [8, 8, 1, 2, 9, 3]),
            ([2, 7, 9, 1], [1, 9, 7, 2]),
            ([6, 3, 1, 8, 6, 9, 2, 7], [7, 2, 9, 6, 8, 1, 3, 6]),
            ([4, 9, 5, 2, 2, 3, 9], [9, 3, 2, 2, 5, 9, 4]),
        ]


class Sort(RandomListTask):
    """
    Original list sorted in increasing order, preserving repeats.
    """
    name = 'sort'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return list(sorted(x))

    @property
    def unit_tests(self):
        return [
            ([3, 9, 3, 8, 2, 7], [2, 3, 3, 7, 8, 9]),
            ([8, 8, 1, 3], [1, 3, 8, 8]),
            ([7, 3, 1, 4, 4, 1, 1, 9, 7, 1, 7, 1], [1, 1, 1, 1, 1, 3, 4, 4, 7, 7, 7, 9]),
        ]


class Unique(RandomListTask):
    """
    Remove duplicates from the original list, preserving order.
    """
    name = 'unique'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return list(dict.fromkeys(x))

    @property
    def unit_tests(self):
        return [
            ([2, 1, 2, 2, 1], [2, 1]),
            ([3, 1, 4], [3, 1, 4]),
            ([3, 3, 3], [3]),
            ([5, 9, 5, 4, 9, 2, 3], [5, 9, 4, 2, 3]),
        ]


class Sum(RandomListTask):
    """
    Sum from the original list.
    """
    name = 'sum'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return [sum(x)]

    @property
    def unit_tests(self):
        return [
            ([1, 2, 3], [6]),
            ([1, 2, 3, 4, 5], [15]),
            ([7, 9, 3], [19]),
            ([], [0]),
        ]


class Product(RandomListTask):
    """
    Product from the original list.
    """
    name = 'product'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        if not x:
            return [0]
        return [reduce(lambda a, b: a * b, x)]

    @property
    def unit_tests(self):
        return [
            ([2, 0, 4, 0, 3, 1, 3, 7, 0, 3, 3], [0]),
            ([1, 2, 3], [6]),
            ([1, 2, 3, 4, 5], [120]),
            ([7, 9, 3], [189]),
            ([], [0]),
        ]


class ConstEmpty(RandomListTask):
    """
    Const nil: always give back ()
    """
    name = 'const_empty'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return []

    @property
    def unit_tests(self):
        return [
            ([], []),
            ([1, 2, 3], []),
            ([5, 9, 4, 17], []),
            ([3, 1, 4, 1, 5, 9], []),
        ]


class Const3(RandomListTask):
    """
    Const 3: always give back (3)
    """
    name = 'const_3'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return [3]

    @property
    def unit_tests(self):
        return [
            ([], [3]),
            ([1, 2, 3], [3]),
            ([5, 9, 4, 17], [3]),
            ([3, 1, 4, 1, 5, 9], [3]),
        ]


class Const123(RandomListTask):
    """
    Const (1 2 3): always give back (1 2 3)
    """
    name = 'const_1_2_3'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return [1, 2, 3]

    @property
    def unit_tests(self):
        return [
            ([], [1, 2, 3]),
            ([1, 2, 3], [1, 2, 3]),
            ([5, 9, 4, 17], [1, 2, 3]),
            ([3, 1, 4, 1, 5, 9], [1, 2, 3]),
        ]


class RepeatFirstFirst(RandomListTask):
    name = 'repeat_first_first_times'
    input_type = ListOfInts
    output_type = ListOfInts
    min_len = 1
    max_len = 1

    def func(self, x):
        x0 = x[0]
        return [x0 for _ in range(x0)]

    @property
    def unit_tests(self):
        return [
            ([2], [2, 2]),
            ([5], [5, 5, 5, 5, 5]),
        ]


class RepeatFirstSecond(RandomListTask):
    name = 'repeat_first_second_times'
    input_type = ListOfInts
    output_type = ListOfInts
    min_len = 2
    max_len = 2

    def func(self, x):
        x0 = x[0]
        x1 = x[1]
        return [x0 for _ in range(x1)]

    @property
    def unit_tests(self):
        return [
            ([2, 2], [2, 2]),
            ([2, 3], [2, 2, 2]),
            ([5, 5], [5, 5, 5, 5, 5]),
            ([5, 1], [5]),
        ]


class RepeatMaxMin(RandomListTask):
    name = 'repeat_max_min_times'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        if not x:
            return []
        return [max(x) for _ in range(min(x))]

    @property
    def unit_tests(self):
        return [
            ([6, 7, 4, 9, 9, 3], [9, 9, 9]),
            ([7, 0, 0, 1, 5], []),
            ([2, 1], [2]),
            ([8, 6, 4], [8, 8, 8, 8]),
        ]


class RepeatIndex5Index3Times(RandomListTask):
    name = 'repeat_index_5_index_3_times'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        if len(x) < 6:
            return []
        return [x[5] for _ in range(x[3])]

    @property
    def unit_tests(self):
        return [
            ([6, 7, 4, 9, 9, 3], [3, 3, 3, 3, 3, 3, 3, 3, 3]),
            ([7, 0, 0, 1, 5], []),
            ([2, 1], []),
            ([8, 6, 4], []),
            ([0, 9, 2, 4, 4, 5], [5, 5, 5, 5]),
            ([0, 1, 2, 3, 4, 3], [3, 3, 3]),
        ]


class CountUp(RandomListTask):
    name = 'count_up_to_n'
    input_type = ListOfInts
    output_type = ListOfInts
    min_len = 1
    max_len = 1

    def func(self, x):
        return list(range(1, x[0] + 1))

    @property
    def unit_tests(self):
        return [
            ([1], [1]),
            ([5], [1, 2, 3, 4, 5]),
            ([3], [1, 2, 3]),
        ]


class CountDown(RandomListTask):
    name = 'count_down_from_n'
    input_type = ListOfInts
    output_type = ListOfInts
    min_len = 1
    max_len = 1

    def func(self, x):
        return list(range(x[0], 0, -1))

    @property
    def unit_tests(self):
        return [
            ([2], [2, 1]),
            ([5], [5, 4, 3, 2, 1]),
        ]


class CountDownBy2(RandomListTask):
    name = 'count_down_from_n_by_2'
    input_type = ListOfInts
    output_type = ListOfInts
    min_len = 1
    max_len = 1

    def func(self, x):
        return list(range(x[0], 0, -2))

    @property
    def unit_tests(self):
        return [
            ([6], [6, 4, 2]),
            ([9], [9, 7, 5, 3, 1]),
            ([18], [18, 16, 14, 12, 10, 8, 6, 4, 2]),
        ]


class Prepend0(RandomListTask):
    name = 'prepend_0'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return [0] + x

    @property
    def unit_tests(self):
        return [
            ([3], [0, 3]),
            ([0, 4], [0, 0, 4]),
            ([], [0]),
            ([6, 7, 4, 9, 9, 3], [0, 6, 7, 4, 9, 9, 3]),
            ([7, 0, 0, 1, 5], [0, 7, 0, 0, 1, 5]),
            ([2, 1], [0, 2, 1]),
            ([8, 6, 4], [0, 8, 6, 4]),
            ([6, 2], [0, 6, 2]),
            ([9, 6, 9, 8], [0, 9, 6, 9, 8]),
            ([9], [0, 9]),
        ]


class Prepend123(RandomListTask):
    name = 'prepend_123'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return [1, 2, 3] + x

    @property
    def unit_tests(self):
        return [
            ([2, 1, 3, 9, 2], [1, 2, 3, 2, 1, 3, 9, 2]),
            ([], [1, 2, 3]),
            ([5, 7, 1], [1, 2, 3, 5, 7, 1]),
            ([7, 4], [1, 2, 3, 7, 4]),
        ]


class Append3(RandomListTask):
    name = 'append_3'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return x + [3]

    @property
    def unit_tests(self):
        return [
            ([0, 0, 6], [0, 0, 6, 3]),
            ([0, 9, 2, 4, 4, 5], [0, 9, 2, 4, 4, 5, 3]),
            ([5, 3, 8, 2], [5, 3, 8, 2, 3]),
            ([7, 1, 3], [7, 1, 3, 3]),
            ([5], [5, 3]),
            ([2, 1, 2, 3, 9], [2, 1, 2, 3, 9, 3]),
            ([6], [6, 3]),
            ([9, 3, 6, 8, 3], [9, 3, 6, 8, 3, 3]),
            ([5, 1, 4, 1], [5, 1, 4, 1, 3]),
            ([1, 6, 8], [1, 6, 8, 3]),
        ]


class Append123(RandomListTask):
    name = 'append_123'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return x + [1, 2, 3]

    @property
    def unit_tests(self):
        return [
            ([2, 1, 3, 9, 2], [2, 1, 3, 9, 2, 1, 2, 3]),
            ([], [1, 2, 3]),
            ([5, 7, 1], [5, 7, 1, 1, 2, 3]),
            ([7, 4], [7, 4, 1, 2, 3]),
        ]


class RotateLeft1(RandomListTask):
    name = 'rotate_left_1'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        if len(x) < 1:
            return []
        return x[1:] + [x[0]]

    @property
    def unit_tests(self):
        return [
            ([1, 4, 1, 4, 2, 9], [4, 1, 4, 2, 9, 1]),
            ([2, 7, 3, 1], [7, 3, 1, 2]),
            ([4, 1, 2, 3, 5, 9, 8], [1, 2, 3, 5, 9, 8, 4]),
            ([3, 3, 4], [3, 4, 3]),
            ([7, 9, 3, 5, 2, 19, 1, 2, 0, 2], [9, 3, 5, 2, 19, 1, 2, 0, 2, 7]),
            ([6, 3, 2, 3, 4, 1, 6, 9], [3, 2, 3, 4, 1, 6, 9, 6]),
            ([1, 4, 3, 8, 3, 8], [4, 3, 8, 3, 8, 1]),
        ]


class RotateRight1(RandomListTask):
    name = 'rotate_right_1'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        if len(x) < 1:
            return []
        return [x[-1]] + x[:-1]

    @property
    def unit_tests(self):
        return [
            ([1, 4, 1, 4, 2, 9], [9, 1, 4, 1, 4, 2]),
            ([2, 7, 3, 1], [1, 2, 7, 3]),
            ([4, 1, 2, 3, 5, 9, 8], [8, 4, 1, 2, 3, 5, 9]),
            ([3, 3, 4], [4, 3, 3]),
            ([7, 9, 3, 5, 2, 19, 1, 2, 0, 2], [2, 7, 9, 3, 5, 2, 19, 1, 2, 0]),
            ([6, 3, 2, 3, 4, 1, 6, 9], [9, 6, 3, 2, 3, 4, 1, 6]),
            ([1, 4, 3, 8, 3, 8], [8, 1, 4, 3, 8, 3]),
        ]


class RotateRightHeadElements(RandomListTask):
    name = 'rotate_right_head_elements'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        if len(x) < 1:
            return []
        head = x[0]
        return [x[(i - head) % len(x)] for i, _ in enumerate(x)]

    @property
    def unit_tests(self):
        return [
            ([2, 6, 8, 2, 4], [2, 4, 2, 6, 8]),
            ([3, 1, 7, 2], [1, 7, 2, 3]),
            ([2, 1, 7, 3], [7, 3, 2, 1]),
            ([1, 9, 3], [3, 1, 9]),
            ([2, 1, 3], [1, 3, 2]),
            ([3, 1, 3], [3, 1, 3]),
            ([8, 1, 3], [1, 3, 8]),
            ([3, 2, 4, 3], [2, 4, 3, 3]),
            ([5, 3, 5, 2, 19, 1, 2, 0, 2], [19, 1, 2, 0, 2, 5, 3, 5, 2]),
            ([7, 3, 2, 3, 4, 1, 6, 9], [3, 2, 3, 4, 1, 6, 9, 7]),
            ([3, 2, 3, 4, 1, 6, 9, 7], [6, 9, 7, 3, 2, 3, 4, 1]),
            ([4, 4, 3, 8, 3, 8, 7], [8, 3, 8, 7, 4, 4, 3]),
        ]


class Append0AppendReversed(RandomListTask):
    name = 'append_0_append_reversed'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return x + [0] + list(reversed(x))

    @property
    def unit_tests(self):
        return [
            ([8], [8, 0, 8]),
            ([9, 6, 8, 2, 4], [9, 6, 8, 2, 4, 0, 4, 2, 8, 6, 9]),
            ([3, 1, 7, 2], [3, 1, 7, 2, 0, 2, 7, 1, 3]),
            ([5], [5, 0, 5]),
            ([9], [9, 0, 9]),
            ([8, 9, 3], [8, 9, 3, 0, 3, 9, 8]),
            ([3], [3, 0, 3]),
            ([7], [7, 0, 7]),
            ([3, 2, 4, 3], [3, 2, 4, 3, 0, 3, 4, 2, 3]),
            ([3, 5, 7], [3, 5, 7, 0, 7, 5, 3]),
        ]


# TODO:
#
# Insert (second xs) (first xs) xs
#
# (9 1) - (9)
# (9 1 3) - (9 3)
# (7 2 4) - (4 7)
# (5 4 3 1 5 6 8 3) - (3 1 5 6 5 8 3)
#
# Append (if (== (head xs) 8) ‘(8) ‘()) (Prepend (if (== (head xs) 8) ‘(8) ‘()) xs): Conditionally bracket with 8s
#
# (8 8) -> (8 8)
# (3 4 6 6 2 8) -> (8 3 4 6 6 2 8)
# (9 4 6 7 7 8) -> (8 9 4 6 7 7 8)
# (8 1 5) -> (8 1 5 8)
# (8 2 2 7 7 3) -> (8 2 2 7 7 3 8)
# (8 3 8 1 4 3) -> (8 3 8 1 4 3 8)
# (4 3 2 8) -> (8 4 3 2 8)
# (7 7 5 7 8) -> (8 7 7 5 7 8)
# (8 2 7 7) -> (8 2 7 7 8)
# (9 5 1 1 5) -> (8 9 5 1 1 5 8)


class Insert1s(RandomListTask):
    name = 'insert_1_after_each_element'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return [j for i in x for j in [i, 1]]

    @property
    def unit_tests(self):
        return [
            ([6, 2, 7], [6, 1, 2, 1, 7, 1]),
            ([8, 8, 1, 3], [8, 1, 8, 1, 1, 1, 3, 1]),
        ]


class InsertIndex(RandomListTask):
    name = 'insert_index_after_each_element'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return [j for i, n in enumerate(x, start=1) for j in [n, i]]

    @property
    def unit_tests(self):
        return [
            ([6, 2, 7], [6, 1, 2, 2, 7, 3]),
            ([8, 8, 1, 3], [8, 1, 8, 2, 1, 3, 3, 4]),
        ]


class FirstElement(RandomListTask):
    name = 'first'
    input_type = ListOfInts
    output_type = ListOfInts
    min_len = 1

    def func(self, x):
        return [x[0]]

    @property
    def unit_tests(self):
        return [
            ([3, 9, 3, 8, 2, 7], [3]),
            ([8, 8, 1, 3], [8]),
            ([7, 3, 1, 4, 4, 1, 1, 9, 7, 1, 7, 1], [7]),
            ([2, 7, 9, 1], [2]),
            ([6, 3, 1, 8, 6, 2, 7], [6]),
            ([4, 9, 5, 2, 2, 3, 9], [4]),
        ]


class SecondElement(RandomListTask):
    name = 'second'
    input_type = ListOfInts
    output_type = ListOfInts
    min_len = 2

    def func(self, x):
        return [x[1]]

    @property
    def unit_tests(self):
        return [
            ([3, 9, 3, 8, 2, 7], [9]),
            ([8, 8, 1, 3], [8]),
            ([7, 3, 1, 4, 4, 1, 1, 9, 7, 1, 7, 1], [3]),
            ([2, 7, 9, 1], [7]),
            ([6, 3, 1, 8, 6, 2, 7], [3]),
            ([4, 9, 5, 2, 2, 3, 9], [9]),
        ]


class ThirdElement(RandomListTask):
    name = 'third'
    input_type = ListOfInts
    output_type = ListOfInts
    min_len = 3

    def func(self, x):
        return [x[2]]

    @property
    def unit_tests(self):
        return [
            ([3, 9, 3, 8, 2, 7], [3]),
            ([8, 8, 1, 3], [1]),
            ([7, 3, 1, 4, 4, 1, 1, 9, 7, 1, 7, 1], [1]),
            ([2, 7, 9, 1], [9]),
            ([6, 3, 1, 8, 6, 2, 7], [1]),
            ([4, 9, 5, 2, 2, 3, 9], [5]),
        ]


class LastElement(RandomListTask):
    name = 'last'
    input_type = ListOfInts
    output_type = Integer
    min_len = 1

    def func(self, x):
        return [x[-1]]

    @property
    def unit_tests(self):
        return [
            ([6, 4, 9, 1, 4], [4]),
            ([7, 3, 3, 2], [2]),
            ([8, 1], [1]),
        ]


class HeadthElementOfTail(RandomListTask):
    name = 'headth_element_of_tail'
    input_type = ListOfInts
    output_type = Integer

    def func(self, x):
        if not x:
            raise SkipExample
        head = x[0]
        if head - 1 < 0:
            raise SkipExample
        tail = x[1:]
        try:
            return tail[head - 1]
        except IndexError:
            raise SkipExample

    @property
    def unit_tests(self):
        return [
            ([3, 9, 2, 1, 8, 8], 1),
            ([2, 7, 9, 1], 9),
            ([6, 3, 1, 8, 6, 9, 2, 7], 2),
            ([4, 9, 5, 2, 2, 3, 9], 2),
        ]


class CountHead(RandomListTask):
    name = 'count_head_in_tail'
    input_type = ListOfInts
    output_type = Integer
    num_examples = 100  # fails under 20 examples, trying a higher limit

    def func(self, x):
        if not x:
            raise SkipExample
        head = x[0]
        tail = x[1:]
        return sum(1 for n in tail if n == head)

    @property
    def unit_tests(self):
        return [
            ([9, 2, 6, 4, 9, 1, 9, 9, 3], 3),
            ([3, 1, 7, 3, 9, 1, 3], 2),
            ([6, 7, 1, 2, 9, 1], 0),
        ]


# TODO: what about zeroes?
class FlattenMapRange(RandomListTask):
    name = 'flatten_map_range'
    input_type = ListOfInts
    output_type = ListOfInts
    num_examples = 100  # fails under 20 examples

    def func(self, x):
        return [i for j in list(map(lambda n: range(1, n + 1), x)) for i in j]

    @property
    def unit_tests(self):
        return [
            ([2, 5, 4], [1, 2, 1, 2, 3, 4, 5, 1, 2, 3, 4]),
            ([3, 2], [1, 2, 3, 1, 2]),
        ]


class FlattenMapRangeReversed(RandomListTask):
    name = 'flatten_map_range_reversed'
    input_type = ListOfInts
    output_type = ListOfInts
    num_examples = 100  # fails under 20 examples

    def func(self, x):
        return [i for j in list(map(lambda n: reversed(range(1, n + 1)), x)) for i in j]

    @property
    def unit_tests(self):
        return [
            ([2, 5, 4], [2, 1, 5, 4, 3, 2, 1, 4, 3, 2, 1]),
            ([3, 2], [3, 2, 1, 2, 1]),
        ]


class FlattenMapRangeSeries(RandomListTask):
    name = 'flatten_map_range_series'
    input_type = ListOfInts
    output_type = ListOfInts
    num_examples = 100  # fails under 20 examples

    def func(self, x):
        if len(x) <= 1:
            return x
        pairs = [(x[a], x[a + 1]) for a in range(len(x) - 1)]

        output = []

        for index, p in enumerate(pairs):
            p0, p1 = p
            if p0 > p1:
                l = range(p0, (p1 - 1), -1)
            elif p0 < p1:
                l = range(p0, (p1 + 1))
            else:
                l = [p0]
            if index != 0 and len(l) > 1:
                # avoid duplicating the same number
                l = l[1:]
            output.extend(l)

        return output

    @property
    def unit_tests(self):
        return [
            ([4, 8, 1, 3], [4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1, 2, 3]),
            ([9, 7, 7, 7, 3, 4, 4, 2, 6], [9, 8, 7, 7, 7, 6, 5, 4, 3, 4, 4, 3, 2, 3, 4, 5, 6]),
            ([3, 2, 1, 2], [3, 2, 1, 2]),
            ([4, 1, 2, 5], [4, 3, 2, 1, 2, 3, 4, 5]),
        ]


class FlattenMapRangeHead(RandomListTask):
    name = 'flatten_map_range_head'
    input_type = ListOfInts
    output_type = ListOfInts
    num_examples = 100  # fails under 20 examples

    def func(self, x):
        if len(x) <= 1:
            return x

        head = x[0]
        tail = x[1:]
        output = []

        for index, val in enumerate(tail):
            if head < val:
                l = range(head, (val + 1))
            else:
                if index == 0:
                    l = [head, val]
                else:
                    l = [val]
            output.extend(l)

        return output

    @property
    def unit_tests(self):
        return [
            ([4, 8, 1, 3], [4, 5, 6, 7, 8, 1, 3]),
            ([5, 1, 9, 7, 7, 3, 4, 4, 2, 6], [5, 1, 5, 6, 7, 8, 9, 5, 6, 7, 5, 6, 7, 3, 4, 4, 2, 5, 6]),
            ([1, 3, 6, 2], [1, 2, 3, 1, 2, 3, 4, 5, 6, 1, 2]),
            ([3, 1, 2, 9], [3, 1, 2, 3, 4, 5, 6, 7, 8, 9]),
            ([4, 8, 1, 7], [4, 5, 6, 7, 8, 1, 4, 5, 6, 7]),
            ([3, 1, 9, 7, 3, 4, 4, 2, 6], [3, 1, 3, 4, 5, 6, 7, 8, 9, 3, 4, 5, 6, 7, 3, 3, 4, 3, 4, 2, 3, 4, 5, 6]),
            ([7, 1, 2, 9], [7, 1, 2, 7, 8, 9]),
        ]


class CumulativeProduct(RandomListTask):
    name = 'cumulative_product'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        last = 1
        output = []
        for n in x:
            last = n * last
            output.append(last)
        return output

    @property
    def unit_tests(self):
        return [
            ([2, 5, 8, 1, 2], [2, 10, 80, 80, 160]),
        ]


class CumulativeSum(RandomListTask):
    name = 'cumulative_sum'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        last = 0
        output = []
        for n in x:
            last = n + last
            output.append(last)
        return output

    @property
    def unit_tests(self):
        return [
            ([2, 5, 8, 1, 2], [2, 7, 15, 16, 18]),
        ]


class FlattenMapRepeatN(RandomListTask):
    name = 'flatten_map_repeat_n_n_times'
    input_type = ListOfInts
    output_type = ListOfInts
    num_examples = 100  # fails under 20 examples

    def func(self, x):
        return [i for i in x for _ in range(i)]

    @property
    def unit_tests(self):
        return [
            ([3, 1, 6], [3, 3, 3, 1, 6, 6, 6, 6, 6, 6]),
        ]


class CountRunLengths(RandomListTask):
    """
    Replace each run of identical elements with the element and the length of the run.
    """
    name = 'count_run_lengths'
    input_type = ListOfInts
    output_type = ListOfInts

    class OrderedCounter(Counter, OrderedDict):
        """Counter that remembers the order elements are first encountered"""

    def func(self, x):
        c = self.OrderedCounter()
        for n in x:
            c[n] += 1
        return [i for k,v in c.items() for i in [k, v]]

    @property
    def unit_tests(self):
        return [
            ([8, 8, 1, 3], [8, 2, 1, 1, 3, 1]),
            ([9, 7, 7, 7, 3, 4, 4, 1, 1, 1, 1, 1], [9, 1, 7, 3, 3, 1, 4, 2, 1, 5]),
        ]


class IndexCounter(RandomListTask):
    """
    For the list xs, create a list, ys, with as many elements
    as the largest element in the list, then set ys[i] to be
    equal to the number of elements in xs equal to i.
    """
    name = 'index_counter'
    input_type = ListOfInts
    output_type = ListOfInts
    min_val = 1  # set min val to 1 since examples don't cover 0

    def func(self, x):
        if not x:
            raise SkipExample
        output = [0 for _ in range(max(x))]
        for n in x:
            output[n - 1] += 1
        return output

    @property
    def unit_tests(self):
        return [
            ([8, 8, 1, 3], [1, 0, 1, 0, 0, 0, 0, 2]),
            ([9, 7, 7, 7, 3, 4, 4, 1, 1, 1, 1, 1], [5, 0, 1, 2, 0, 0, 3, 0, 1]),
            ([3, 2, 1, 2], [1, 2, 1]),
            ([4, 1, 2, 2, 2, 1], [2, 3, 0, 1]),
        ]


class AddNtoNthElement(RandomListTask):
    """
    Add n to the nth element, starting from 0.
    """
    name = 'add_n_to_nth_element'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return [n + index for index, n in enumerate(x)]

    @property
    def unit_tests(self):
        return [
            ([6, 2, 7], [6, 3, 9]),
            ([8, 8, 1, 3], [8, 9, 3, 6]),
            ([3, 9, 3, 8, 1, 7], [3, 10, 5, 11, 5, 12]),
        ]


class ReverseAndAddNtoNthElement(RandomListTask):
    """
    Reverse the list, then add n to the nth element starting from 0.
    """
    name = 'reverse_and_add_n_to_nth_element'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return [n + index for index, n in enumerate(list(reversed(x)))]

    @property
    def unit_tests(self):
        return [
            ([6, 2, 7], [7, 3, 8]),
            ([8, 8, 1, 3], [3, 2, 10, 11]),
            ([3, 9, 3, 8, 2, 7], [7, 3, 10, 6, 13, 8]),
        ]


class CountNumbersAndSort(RandomListTask):
    """
    A flattened list of pairs (k n_k) specifying each distinct number k
    in the original list, followed by the number of times n_k that number k
    appears in the original list, in increasing order k.
    """
    name = 'count_numbers_and_sort_by_number'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        c = Counter()
        for n in x:
            c[n] += 1
        return [i for k, v in sorted(c.items()) for i in [k, v]]

    @property
    def unit_tests(self):
        return [
            ([3, 9, 3, 8, 2, 7], [2, 1, 3, 2, 7, 1, 8, 1, 9, 1]),
            ([8, 8, 1, 3], [1, 1, 3, 1, 8, 2]),
            ([7, 3, 1, 4, 4, 1, 1, 9, 7, 1, 7, 1], [1, 5, 3, 1, 4, 2, 7, 3, 9, 1]),
        ]


class SortAndDedupe(RandomListTask):
    """
    Original list sorted in increasing order, without repeats.
    """
    name = 'sort_and_dedupe'
    input_type = ListOfInts
    output_type = ListOfInts

    def func(self, x):
        return list(sorted(set(x)))

    @property
    def unit_tests(self):
        return [
            ([3, 9, 3, 8, 2, 7], [2, 3, 7, 8, 9]),
            ([8, 8, 1, 3], [1, 3, 8]),
            ([7, 3, 1, 4, 4, 1, 1, 9, 7, 1, 7, 1], [1, 3, 4, 7, 9]),
        ]


def reformat_examples(example_str):
    """
    Use to convert examples in Josh's Google Doc to Python format for unit tests.
    """
    lines = example_str.split('\n')
    lines = [l.strip() for l in lines]
    lines = list(filter(None, lines))
    out = []
    for line in lines:
        line = line.replace('(', '[')
        line = line.replace(')', ']')
        if '->' in line:
            split_char = '->'
        elif '-' in line:
            split_char = '-'
        else:
            raise ValueError('Missing split char in line: {}'.format(line))
        i, o = line.split(split_char)
        i = i.strip()
        i = i.replace(' ', ', ')
        o = o.strip()
        o = o.replace(' ', ', ')
        out.append('    (' + i + ', ' + o + '),')
    print('\n'.join(out))
    return out


def generate_multiple(task_cls, count):
    subtasks = []
    for i in range(count):
        t = task_cls()
        t.name = t.name + '_' + str(i)
        subtasks.append(t)
    return subtasks


def create_more_list_tasks():
    tasks = [
        Length(),
        IsEmpty(),
        Max(),
        Min(),
        Reverse(),
        Sort(),
        Unique(),
        Sum(),
        Product(),
        ConstEmpty(),
        Const3(),
        Const123(),
        RepeatFirstFirst(),
        RepeatFirstSecond(),
        RepeatMaxMin(),
        RepeatIndex5Index3Times(),
        CountUp(),
        CountDown(),
        CountDownBy2(),
        Prepend0(),
        Prepend123(),
        Append3(),
        Append123(),
        RotateLeft1(),
        RotateRight1(),
        RotateRightHeadElements(),
        Append0AppendReversed(),
        Insert1s(),
        InsertIndex(),
        FirstElement(),
        SecondElement(),
        ThirdElement(),
        LastElement(),
        HeadthElementOfTail(),
        CountHead(),
        FlattenMapRange(),
        FlattenMapRangeReversed(),
        FlattenMapRangeSeries(),
        FlattenMapRangeHead(),
        CumulativeProduct(),
        CumulativeSum(),
        FlattenMapRepeatN(),
        CountRunLengths(),
        IndexCounter(),
        AddNtoNthElement(),
        ReverseAndAddNtoNthElement(),
        CountNumbersAndSort(),
        SortAndDedupe(),
    ]

    # shuffle
    random.shuffle(tasks)

    names = []
    data = []
    for t in tasks:
        assert t.name not in names, f'Multiple tasks with the same name ({t.name}) exist!'
        names.append(t.name)
        data.append(t.json())

    with open(JSON_FILE, 'w') as f:
        json.dump(data, f)

    num_tasks = len(tasks)
    print(f'wrote {num_tasks} tasks to: {JSON_FILE}')


if __name__ == '__main__':
    create_more_list_tasks()
