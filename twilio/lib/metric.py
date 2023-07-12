""" Publish metric to SNS. """

import sns_client
import util

def event_to_endpoint(event):
    """
    Return an endpoint appropriate for a metric from
    From or To.
    """
    extension = util.sip_to_extension(event['From'])
    if extension:
        # Outgoing from Twilio SIP Domain,
        # From is SIP URI to extension.
        return extension
    else:
        # Incoming to Twilio phone number,
        # To is E.164 of caller.
        extensions = util.get_extensions()
        return util.e164_to_extension(event['To'], extensions)

def publish(user_event, event, env):
    channel = event_to_endpoint(event)
    util.log('metric {} {}'.format(channel, user_event))
    return sns_client.publish(channel, user_event, env)
