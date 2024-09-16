from unittest import mock, TestCase

from chalicelib import env_util
from chalicelib import ops

env = env_util.get_env()


class TestOps(TestCase):

    def test_exercise(self):
        call = ops._exercise("stage", "clinton", env)
