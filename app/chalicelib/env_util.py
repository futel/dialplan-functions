import dotenv
import json
import os

dotenv.load_dotenv(os.path.join(
    os.path.dirname(__file__), 'environment', '.env'))

def get_env():
    normal_variables = {
        'ASSET_HOST': os.environ['ASSET_HOST'],
        'AWS_DEFAULT_REGION': os.environ['AWS_DEFAULT_REGION'],
        'AWS_TOPIC_ARN': os.environ['AWS_TOPIC_ARN'],
        'nanpa_sisyphus': os.environ['nanpa_sisyphus'],
        'TWILIO_ACCOUNT_SID': os.environ['TWILIO_ACCOUNT_SID'],
        'TWILIO_AUTH_TOKEN': os.environ['TWILIO_AUTH_TOKEN']}
    json_variables = {
        'operator_numbers': os.environ['operator_numbers']}
    json_variables = {k:json.loads(v) for (k,v) in json_variables.items()}
    return {**normal_variables, **json_variables}

def get_extensions():
    """Return extensions asset object."""
    filename = os.path.join(
        os.path.dirname(__file__), 'assets', 'extensions.json')
    with open(filename) as f:
        return json.load(f)

def get_ivrs():
    """Return ivrs asset object."""
    out = {}
    srcs = [
        'ivrs_directories',
        'ivrs_operator',
        'ivrs_outgoing',
        'ivrs_utilities']
    for src in srcs:
        path = '{}.json'.format(src)
        path = os.path.join(
            os.path.dirname(__file__), 'assets', path)
        with open(path) as f:
            out.update(json.load(f))
    return out
