from unittest import mock, TestCase

from chalicelib import env_util
from chalicelib import ops

env = env_util.get_env()

stage = "stage"
extension = "test-one"


class TestOps(TestCase):

    def test_exercise(self):
        """Exercise an arbitrary extension on stage."""
        call = ops.exercise_one(stage, extension, "community_outgoing", env)
