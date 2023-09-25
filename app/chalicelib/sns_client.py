import datetime
import json

from . import util

metric_host_base = 'dialplan-functions';

def get_metric_hostname(request):
    """
    Return the appropriate metric event endpoint name for this request.
    """
    return metric_host_base + '-' + util.get_instance(request)

def event_to_message(endpoint, user_event, hostname):
    date_string = datetime.datetime.now().isoformat()
    event = {
        'Event': 'UserEvent',
        'endpoint': endpoint,
        'Channel': endpoint,    # Can probably be removed.
        'UserEvent': user_event}
    message = {
        'timestamp': date_string,
        'hostname': hostname,
        'event': event}
    return message

def publish(endpoint, user_event, request, env):
    hostname = get_metric_hostname(request)
    message = event_to_message(endpoint, user_event, hostname)
    return env['sns_client'].publish(
        TargetArn=env['AWS_TOPIC_ARN'],
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json')
