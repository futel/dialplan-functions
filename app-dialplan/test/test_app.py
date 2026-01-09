from unittest import TestCase

import app


class TestAccumulateList(TestCase):
    """Unit tests for app._accumulate_list (or fallback to _accumulate_dict)."""

    def test_single_pair(self):
        pairs = [('a', '1')]
        got = app._accumulate_dict(pairs)
        self.assertEqual(got, {'a': '1'})

    def test_multiple_distinct_keys(self):
        pairs = [('a', '1'), ('b', '2')]
        got = app._accumulate_dict(pairs)
        self.assertEqual(got, {'a': '1', 'b': '2'})

    def test_duplicate_keys_become_list(self):
        pairs = [('a', '1'), ('a', '2'), ('b', '3')]
        got = app._accumulate_dict(pairs)
        # 'a' should be converted to a list preserving insertion order
        self.assertEqual(got, {'a': ['1', '2'], 'b': '3'})

    def test_three_duplicates(self):
        pairs = [('x', '1'), ('x', '2'), ('x', '3')]
        got = app._accumulate_dict(pairs)
        self.assertEqual(got, {'x': ['1', '2', '3']})

    def test_empty_input(self):
        pairs = []
        got = app._accumulate_dict(pairs)
        self.assertEqual(got, {})
