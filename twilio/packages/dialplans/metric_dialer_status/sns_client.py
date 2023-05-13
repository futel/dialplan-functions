import boto3
import datetime
import json
import os

import util


metric_host_base = 'do-dialplans';

def getenv():
    return {
        'AWS_ACCESS_KEY_ID': os.environ['AWS_ACCESS_KEY_ID'],
        'AWS_SECRET_ACCESS_KEY': os.environ['AWS_SECRET_ACCESS_KEY'],
        'AWS_TOPIC_ARN': os.environ['AWS_TOPIC_ARN']}

# Return the appropriate metric event hostname for our environment.
def get_metric_hostname():
    return metric_host_base + '-' + util.get_instance()

def event_to_message(event, hostname):
    date_string = datetime.datetime.now().isoformat()
    event = {
        'Event': 'UserEvent',
        'Channel': event['channel'],
        'UserEvent': event['user_event']}
    message = {
        'timestamp': date_string,
        'hostname': hostname,
        'event': event}
    return message

def publish(event, env):
    hostname = get_metric_hostname()
    message = event_to_message(event, hostname)
    client = boto3.client(
        'sns',
        aws_access_key_id=env['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=env['AWS_SECRET_ACCESS_KEY'],
        region_name= 'us-west-2')
    return client.publish(
        TargetArn=env['AWS_TOPIC_ARN'],
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json')
