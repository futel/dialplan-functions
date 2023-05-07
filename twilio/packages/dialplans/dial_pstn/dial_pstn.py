# TwiML dialer suitable as the destination for a TwiML <redirect> verb.

from twilio.twiml.voice_response import VoiceResponse

import util

def dial_pstn(event, context):
    """Return TwiML to dial number with attributes from event."""
    number = event['number']
    caller_id = event['caller_id']
    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        caller_id=caller_id,
        answer_on_bridge=True,
        action=util.function_url(context, 'dialer_status'))
    dial.number(number)
    response.append(dial)
    return util.twiml_response(response)
