"""
Functions for ops HTTP endpoints.
"""

from . import sns_client

def log(request, env):
    message = {'hello': 'world'}
    #return sns_client.publish(message, env)
    return message
