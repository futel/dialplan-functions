from . import sns_client
from . import util


def request_to_endpoint(request):
    """
    Return an endpoint appropriate for a metric from
    From or To.
    """
    extension = util.sip_to_extension(request.post_fields['From'])
    if extension:
        # Outgoing from Twilio SIP Domain,
        # From is SIP URI to extension.
        return extension
    else:
        # Incoming to Twilio phone number,
        # To is E.164 of caller.
        extensions = util.get_extensions()
        return util.e164_to_extension(
            request.post_fields['From'], extensions)

def publish(user_event, request, env):
    channel = request_to_endpoint(request)
    util.log('metric {} {}'.format(channel, user_event))
    return sns_client.publish(channel, user_event, request, env)
