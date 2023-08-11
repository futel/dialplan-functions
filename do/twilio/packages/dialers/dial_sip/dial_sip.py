"""
Return TwiML to dial a SIP URI pointing to Asterisk server.
"""

# TwiML dialer suitable as the destination for a TwiML <redirect> verb.

from twilio.twiml.voice_response import VoiceResponse

import metric
import util

extensions = util.get_extensions()

def dial_sip(event, context, env):
    """Return TwiML to dial a SIP URI pointing to Asterisk server."""
    metric.publish('dial_sip', event, env)
    from_uri = event['From']
    to_uri = event['To']

    # XXX are these already sip_to_extension?
    from_extension = util.sip_to_extension(from_uri)
    to_extension = util.sip_to_extension(to_uri)
    if to_extension == "#":
        to_extension = extensions[from_extension]['outgoing']
    elif to_extension == "0":
        to_extension = 'operator'

    response = util.dial_sip_futel(
        to_extension, from_extension, context, env)
    return util.twiml_response(response)
