import datetime

from . import sns_client
from . import util

metric_host_base = 'dialplan-functions'

def request_to_endpoint(request, env):
    """
    Return an endpoint appropriate for a metric from From.
    """
    extension = util.sip_to_extension(request.post_fields['From'])
    if extension:
        # Outgoing from Twilio SIP Domain,
        # From is SIP URI to extension.
        return extension
    extension =  util.e164_to_extension(
        request.post_fields['To'], env['extensions'])
    if extension:
        # Incoming PSTN call to Twilio phone number,
        # To is E.164 of caller.
        return extension
    extension =  util.e164_to_extension(
        request.post_fields['From'], env['extensions'])
    if extension:
        # Outgoing PSTN call started by the Twilio client.
        # From is E.164 of caller.
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

# Publish takes .1s! Throw it in a worker queue?
def publish(user_event, request, env):
    endpoint = request_to_endpoint(request, env)
    hostname = _get_metric_hostname(request)
    message = _event_to_message(endpoint, user_event, hostname)
    util.log('metric endpoint:{} user_event:{}'.format(endpoint, user_event))
    return sns_client.publish_metric(message, env)
