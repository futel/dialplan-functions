# TwiML dialer suitable as the destination for a TwiML <redirect> verb.
# Determine whether we are dialing a PSTN number or a predetermined SIP
# extension.

from twilio.twiml.voice_response import VoiceResponse

import util

extensions = util.get_extensions()

def dial_outgoing(event, context):
    """Return TwiML to dial SIP URI with attributes from event."""
    util.log('dial_sip')
    from_uri = event['from_uri']
    to_uri = event['to_uri']

    to_extension = util.sip_to_extension(to_uri)
    if to_extension in ('#', '0'):
        function = 'dial_sip'
    else:
        function = 'dial_pstn'
    params = {'to_uri': to_uri, 'from_uri': from_uri}
    response = VoiceResponse()
    response.redirect(
        util.function_url(context, function, params))
    return util.twiml_response(response)
