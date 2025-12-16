import boto3
import dotenv
import json
import os
from twilio.rest import Client

dotenv.load_dotenv(os.path.join(
    os.path.dirname(__file__), 'environment', '.env'))

def get_env():
    env = _get_env_attributes()
    env['extensions'] = _get_extensions()
    env['ivrs'] = _get_ivrs()
    env['twilio_client'] = _get_twilio_client(env)
    env['sns_client'] = boto3.client('sns')
    return env

def _get_env_attributes():
    """Return a map of attributes from the environment."""
    # These are in the environment because they are secrets, or because
    # they are decided at deployment time.
    normal_variables = {
        'ASSET_HOST': os.environ['ASSET_HOST'],
        #'AWS_DEFAULT_REGION': os.environ['AWS_DEFAULT_REGION'],
        #'AWS_LOGS_TOPIC_ARN': os.environ['AWS_LOGS_TOPIC_ARN'],
        'AWS_METRICS_TOPIC_ARN': os.environ['AWS_METRICS_TOPIC_ARN'],
        'nanpa_sisyphus': os.environ['nanpa_sisyphus'],
        'stage': os.environ['stage'],
        'TWILIO_ACCOUNT_SID': os.environ['TWILIO_ACCOUNT_SID'],
        'TWILIO_AUTH_TOKEN': os.environ['TWILIO_AUTH_TOKEN']}
    json_variables = {
        'operator_numbers': os.environ['operator_numbers']}
    json_variables = {k:json.loads(v) for (k,v) in json_variables.items()}
    return {**normal_variables, **json_variables}

def _get_twilio_client(env):
    twilio_account_sid = env['TWILIO_ACCOUNT_SID']
    twilio_auth_token = env['TWILIO_AUTH_TOKEN']
    client = Client(twilio_account_sid, twilio_auth_token)
    return client

def _get_extensions():
    """Return extensions asset object."""
    filename = os.path.join(
        os.path.dirname(__file__), 'assets', 'extensions.json')
    with open(filename) as f:
        return json.load(f)

def _get_ivrs():
    """Return ivrs asset object."""
    out = {}
    srcs = [
        'ivrs_directories',
        'ivrs_operator',
        'ivrs_outgoing',
        'ivrs_incoming',
        'ivrs_utilities',
        'ivrs_streetroots']
    for src in srcs:
        path = '{}.json'.format(src)
        path = os.path.join(
            os.path.dirname(__file__), 'assets', path)
        with open(path) as f:
            out.update(json.load(f))
    return out
