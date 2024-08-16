import dotenv
#import json
import os

dotenv.load_dotenv(os.path.join(
    os.path.dirname(__file__), 'environment', '.env'))

def get_env():
    normal_variables = {
        #'AWS_DEFAULT_REGION': os.environ['AWS_DEFAULT_REGION'],
        #'AWS_LOGS_TOPIC_ARN': os.environ['AWS_LOGS_TOPIC_ARN'],
        #'AWS_METRICS_TOPIC_ARN': os.environ['AWS_METRICS_TOPIC_ARN'],
        'stage': os.environ['stage'],
        'TWILIO_ACCOUNT_SID': os.environ['TWILIO_ACCOUNT_SID'],
        'TWILIO_AUTH_TOKEN': os.environ['TWILIO_AUTH_TOKEN']}
    json_variables = {}
    return {**normal_variables, **json_variables}
