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

# XXX publish takes .23-.55s! Can we async?
#     https://stackoverflow.com/questions/74589325/how-to-make-an-asynchronous-api-call-to-a-chalice-app
def publish(user_event, request, env):
    endpoint = request_to_endpoint(request)
    util.log('metric {} {}'.format(endpoint, user_event))
    return sns_client.publish(endpoint, user_event, request, env)
