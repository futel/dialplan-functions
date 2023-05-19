# Reject call.

from twilio.twiml.voice_response import VoiceResponse

import util

def reject(event, context):
    """Return TwiML reject call."""
    util.log('reject')
    response = VoiceResponse()
    response.say(
        "We're sorry, your call cannot be completed as dialed. "
        "Please check the number and try again.");
    response.reject()
    return util.twiml_response(response)
