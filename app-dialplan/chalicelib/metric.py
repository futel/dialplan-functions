import datetime

from . import sns_client
from . import util

metric_host_base = 'dialplan-functions'
#default_endpoint = "system"

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
    util.log(
        'metric hostname:{} endpoint:{} event:{}'.format(
            hostname, endpoint, event))
    return sns_client.publish_metric(message, env)

# Publish takes .1s! Throw it in a worker queue?
def publish(event, user, request, env):
    """Publish an event from twilio programmable voice."""
    hostname = _get_metric_hostname(request)
    return _publish(event, user, hostname, env)

def publish_twilio_error(event, message, env):
    """Publish an error event."""
    # The event is from a twilio error webhook.
    # Note that all webhooks post to the same prod url, we need to determine
    # what instance/hostname it comes from.
    # 'sip:demo-one@direct-futel-stage.sip.twilio.com'
    url = message['webhook']['request']['url']
    if url:
        # ('sip:demo-one', 'direct-futel-stage.sip.twilio.com')
        (endpoint, host) = url.split('@')
        endpoint = endpoint.split(':')[1] # 'demo-one'
        hostname = host.split('.')[0]      # 'direct-futel-stage'
        # XXX should be dialplan-functions-stage
        hostname = hostname.split('-')[-1] # 'stage'
    else:
        # We get an url of None when we timeout trying to call a registered
        # endpoint, twilio error 32011.
        # '<sip:demo-one@foo:5060>'
        to = message['webhook']['request']['parameters']['To']
        (endpoint, _) = to.split('@')
        endpoint = endpoint[1:] # 'sip:demo-one'
        # The hostname is parseable from the From paramater, but it's ugly.
        # XXX Just assume the worst.
        #'From': '"+15034681337" <sip:+15034681337@direct-futel-prod.sip.twilio.com>;tag=90101523_c3356d0b_8c4a3aa3-3f2a-46be-9504-09b82ef3ea6b'}
        hostname = 'prod'
    hostname = metric_host_base + '-' + hostname
    return _publish(event, endpoint, hostname, env)
