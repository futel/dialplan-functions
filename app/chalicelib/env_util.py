import dotenv
import json
import os

dotenv.load_dotenv(os.path.join(
    os.path.dirname(__file__), 'environment', '.env'))

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
    out = {}
    srcs = ['ivrs_outgoing', 'ivrs_utilities']
    for src in srcs:
        path = '{}.json'.format(src)
        path = os.path.join(
            os.path.dirname(__file__), 'assets', path)
        with open(path) as f:
            out.update(json.load(f))
    return out
