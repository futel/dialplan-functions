# TwiML dialer suitable as the destination for a TwiML <redirect> verb.

from twilio.twiml.voice_response import VoiceResponse

import util

extensions = util.get_extensions()

def dial_pstn(event, context):
    """Return TwiML to dial PSTN number with attributes from event."""
    to_number = event['to_number']
    from_uri = event['from_uri']

    # The caller ID is the SIP extension we are calling from, which we assume is E.164.
    extension = util.sip_to_exension(from_uri)
    caller_id = extensions[extension]['caller_id']

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        caller_id=caller_id,
        answer_on_bridge=True,
        action=util.function_url(context, 'metric_dialer_status'))
    dial.number(to_number)
    return util.twiml_response(response)
