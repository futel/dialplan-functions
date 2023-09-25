import json
import os

def get_env():
    return {
        'ASSET_HOST': os.environ['ASSET_HOST'],
        'AWS_TOPIC_ARN': os.environ['AWS_TOPIC_ARN']}

def get_extensions():
    """Return extensions asset object."""
    filename = os.path.join(
        os.path.dirname(__file__), 'assets', 'extensions.json')
    with open(filename) as f:
        return json.load(f)

def get_ivrs():
    """Return ivrs asset object."""
    filename = os.path.join(
        os.path.dirname(__file__), 'assets', 'ivrs.json')
    with open(filename) as f:
        return json.load(f)
