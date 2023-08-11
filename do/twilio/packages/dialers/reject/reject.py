"""
Return TwiML to reject call.
"""

from twilio.twiml.voice_response import VoiceResponse

import metric
import util

def reject(event, context, env):
    """Return TwiML reject call."""
    metric.publish('reject', event, env)
    response = VoiceResponse()
    response.say(
        "We're sorry, your call cannot be completed as dialed. "
        "Please check the number and try again.");
    response.reject()
    return util.twiml_response(response)
