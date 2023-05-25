""" Publish metric to SNS. """

import sns_client
import util

def event_to_endpoint(event):
    """
    Return an endpoint appropriate for a metric from
    from_uri or to_number
    """
    extension = util.sip_to_extension(event['from_uri'])
    if extension:
        # Outgoing from Twilio SIP Domain,
        # from_uri is SIP URI to extension.
        return extension
    else:
        # Incoming to Twilio phone number,
        # to_uri is E.164 of caller.
        extensions = util.get_extensions()
        return util.e164_to_extension(event['to_uri'], extensions)

def publish(user_event, event, env):
    channel = event_to_endpoint(event)
    util.log('metric {} {}'.format(channel, user_event))
    return sns_client.publish(channel, user_event, env)
