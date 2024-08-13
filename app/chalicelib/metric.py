import datetime

from . import sns_client
from . import util

metric_host_base = 'dialplan-functions'
default_endpoint = "system"

def request_to_endpoint(request, env):
    """
    Return an endpoint appropriate for a metric from From.
    """
    extension = util.sip_to_user(request.post_fields['From'])
    if extension:
        # Call from client to Twilio SIP Domain,
        # From is SIP URI of caller's extension.
        return extension
    extension =  util.e164_to_extension(
        request.post_fields['To'], env['extensions'])
    if extension:
        # Incoming PSTN call to Twilio phone number,
        # To is E.164 being called.
        return extension
    extension =  util.e164_to_extension(
        request.post_fields['From'], env['extensions'])
    if extension:
        # Outgoing PSTN call started by the Twilio client, where From is
        # whatever we tell the client it is, so hopefully it is the E.164 of the
        # "extension" "doing the thing".
        return extension
    util.log(
        'unknown metric extension to:{} from:{}'.format(
            request.post_fields['To'], request.post_fields['From']))
    return None

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

def _publish(event, endpoint, request, env):
    hostname = _get_metric_hostname(request)
    message = _event_to_message(endpoint, event, hostname)
    util.log('metric endpoint:{} event:{}'.format(endpoint, event))
    return sns_client.publish_metric(message, env)

# Publish takes .1s! Throw it in a worker queue?
def publish(event, request, env):
    """Publish an event coming from twilio programmable voice."""
    endpoint = request_to_endpoint(request, env)
    return _publish(event, endpoint, request, env)

def publish_other(event, request, env):
    """Publish an event."""
    return _publish(event, default_endpoint, request, env)
