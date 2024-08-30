import datetime

from . import sns_client
from . import util

metric_host_base = 'dialplan-functions'
default_endpoint = "system"

def _get_metric_hostname(request):
    """
    Return the appropriate metric event endpoint name for this request.
    """
    return metric_host_base + '-' + util.get_instance(request)

def _event_to_message(endpoint, user_event, hostname):
    """Package and return the attributes in an appropriate message dict."""
    date_string = datetime.datetime.now().isoformat()
    # This weird subdict matches the format that asterisk sends.
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

def _publish(event, endpoint, hostname, env):
    message = _event_to_message(endpoint, event, hostname)
    util.log('metric endpoint:{} event:{}'.format(endpoint, event))
    return sns_client.publish_metric(message, env)

# Publish takes .1s! Throw it in a worker queue?
def publish(event, request, env):
    """Publish an event from twilio programmable voice."""
    endpoint = util.request_to_endpoint(request, env)
    hostname = _get_metric_hostname(request)
    return _publish(event, endpoint, hostname, env)

def publish_twilio_error(event, message, env):
    """Publish an error event."""
    # The event is from a twilio error webhook.
    # 'sip:demo-one@direct-futel-stage.sip.twilio.com'
    url = message['webhook']['request']['url']
    host = url.split('@')[1]    # 'direct-futel-stage.sip.twilio.com'
    hostname = host.split('.')[0]      # 'direct-futel-stage'
    hostname = hostname.split('-')[-1] # 'stage'
    return _publish(event, default_endpoint, hostname, env)

def publish_twilio_error(event, message, env):
    """Publish an error event."""
    # The event is from a twilio error webhook.
    # If the event was from a twilio pv dial verb call, we expect url to be a
    # sip address, like 'sip:demo-one@direct-futel-stage.sip.twilio.com'.
    url = message['webhook']['request']['url']
    if url:
        try:
            host = url.split('@')[1]    # 'direct-futel-stage.sip.twilio.com'
            hostname = host.split('.')[0]      # 'direct-futel-stage'
            hostname = hostname.split('-')[-1] # 'stage'
        except Exception:
            # If the event was from a twilio rest api call, we expect url to be
            # the status_callback url, like
            # 'https://stage.dialplans.phu73l.net/metric_dialer_status'.
            host = url.split('//')[1] # 'stage.dialplans.phu73l.net/metric_dialer_status'
            hostname = host.split('.')[0] # 'stage'
    else:
        # We are confused, just assume the worst, we are on prod?
        hostname = "prod"
    return _publish(event, default_endpoint, hostname, env)
