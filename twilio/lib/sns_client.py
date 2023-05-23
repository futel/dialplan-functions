import boto3
import datetime
import json
import os

import util


metric_host_base = 'do-functions';

# Return the appropriate metric event hostname for our environment.
def get_metric_hostname(env):
    return metric_host_base + '-' + util.get_instance(env)

def event_to_message(channel, user_event, hostname):
    date_string = datetime.datetime.now().isoformat()
    event = {
        'Event': 'UserEvent',
        'Channel': channel,
        'UserEvent': user_event}
    message = {
        'timestamp': date_string,
        'hostname': hostname,
        'event': event}
    return message

def publish(channel, user_event, env):
    hostname = get_metric_hostname(env)
    message = event_to_message(channel, user_event, hostname)
    client = boto3.client(
        'sns',
        aws_access_key_id=env['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=env['AWS_SECRET_ACCESS_KEY'],
        region_name= 'us-west-2')
    return client.publish(
        TargetArn=env['AWS_TOPIC_ARN'],
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json')
