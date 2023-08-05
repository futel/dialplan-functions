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
    else:
        # XXX redirect to call cannot be completed as dialed
        raise NotImplementedError

    instance = util.get_instance(env)

    # The caller ID is the SIP extension we are calling from, which we assume is E.164.
    caller_id = extensions[from_extension]['caller_id']
    enable_emergency = extensions[from_extension]['enable_emergency']
    enable_emergency = util.python_to_twilio_param(enable_emergency)

    util.log(f'caller_id: {caller_id}')
    util.log(f'to_extension: {to_extension}')
    util.log(f'enable_emergency: {enable_emergency}')
    util.log(f'instance: {instance}')

    sip_uri = (f'sip:{to_extension}@futel-{instance}.phu73l.net;'
               f'region=us2?x-callerid={caller_id}&x-enableemergency={enable_emergency}')

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        answer_on_bridge=True,
        action=util.function_url(context, 'metric_dialer_status'))
    dial.sip(sip_uri)
    return util.twiml_response(response)
