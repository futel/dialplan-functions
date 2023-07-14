"""
Return TwiML to redirect to the SIP or PSTN dialer.
"""
# We should probably just return the relvant TwiML
# instead of redirecting.

from twilio.twiml.voice_response import VoiceResponse

import metric
import util

extensions = util.get_extensions()

def dial_outgoing(event, context, env):
    """Return TwiML to dial SIP URI with attributes from event."""
    metric.publish('dial_outgoing', event, env)
    from_uri = event['From']
    to_uri = event['To']

    from_extension = util.sip_to_extension(from_uri)
    to_extension = util.sip_to_extension(to_uri)
    if to_extension == '0':
        function = 'dial_sip'
    elif to_extension == '#':
        if extensions[from_extension]['local_outgoing']:
            function = 'ivr'
        else:
            function = 'dial_sip'
    else:
        function = 'dial_pstn'
    params = {'To': to_uri, 'From': from_uri}
    response = VoiceResponse()
    response.redirect(
        util.function_url(context, function, params))
    return util.twiml_response(response)
