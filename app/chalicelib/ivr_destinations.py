"""
Functions reached by IVR menu choices.
"""

from twilio.twiml.voice_response import VoiceResponse

#from . import util

DESTINATIONS = {'enqueue_operator': enqueue_operator}

def get_destination(name):
    """Return the destination function for name."""
    return DESTINATIONS.get(name)

def enqueue_operator(extension, request, env):
    """
    Return TwiML to run an IVR context.
    """
    # XXX hit REST to call all ops here
    #     need callerid
    caller_id = extension['caller_id']
    response = VoiceResponse()
    # XXX statement should be an IVR statement for consistency
    #response.play('xxx') # please hold, must expand sound_url
    response.enqueue('operator') # wait_url, action
