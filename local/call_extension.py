"""
Call an extension with the twilio API and play a dialplan.
"""

from chalicelib import ops
from chalicelib import env_util

env = env_util.get_env()

stage = "stage"
extension = "clinton"
context = "outgoing_operator_operator"

ops.exercise_one(stage, extension, context, env=env)
