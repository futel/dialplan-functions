"""
Functions reached by IVR menu choices.
"""

from twilio.twiml.voice_response import VoiceResponse

from . import ivrs
from . import util

WAIT_FUNCTION = 'enqueue_operator_wait'


def get_destination(name):
    """Return the destination function for name."""
    return DESTINATIONS.get(name)

def outgoing_operator_enqueue(extension, request, env):
    """
    Return TwiML to run an IVR context to put the caller
    in the operator queue.
    """
    caller_id = extension['caller_id']
    response = VoiceResponse()
    # XXX All statements should be in IVRs for validation, but IVRs
    #     aren't flexible enough.
    response.play(
        ivrs.sound_url(
            "please-hold-for-the-next-available-operator",
            "en",
            "operator",
            request,
            env))
    response.enqueue(
        'operator', wait_url=util.function_url(request, WAIT_FUNCTION))
    return response

def outgoing_operator_accept(extension, request, _env):
    """Return TwiML to send the caller to the operator queue."""
    response = VoiceResponse()
    dial = response.dial()
    queue = dial.queue('operator')
    return response


DESTINATIONS = {'outgoing_operator_enqueue': outgoing_operator_enqueue,
                'outgoing_operator_accept': outgoing_operator_accept}
