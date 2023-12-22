"""
Functions reached by IVR menu choices.
"""

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from . import ivrs
from . import util

WAIT_FUNCTION = 'enqueue_operator_wait'
operator_queue_name = 'operator'

def get_destination(name):
    """Return the destination function for name."""
    return DESTINATIONS.get(name)

def friction(request, env):
    # Note that this is the first interaction on handset pickup, so
    # friction should not be configured to block or ignore possible
    # 911 digits.
    return None

def outgoing_operator_enqueue(request, env):
    """
    Return TwiML to run an IVR context to put the call next in line
    in the operator queue.
    """
    response = VoiceResponse()
    response.enqueue(
        operator_queue_name, wait_url=util.function_url(request, WAIT_FUNCTION))
    return response

def outgoing_operator_accept(request, env):
    """Return TwiML to send the call to the next caller in operator queue."""
    lang = request.query_params.get('lang', 'en')
    # Is there still a caller in the queue?
    twilio_account_sid = env['TWILIO_ACCOUNT_SID']
    twilio_auth_token = env['TWILIO_AUTH_TOKEN']
    client = Client(twilio_account_sid, twilio_auth_token)
    for queue in client.queues.list():
        if queue.friendly_name == operator_queue_name:
            if not queue.current_size:
                # Too late, tell the operator.
                dest_c_name = 'outgoing_operator_operator_empty'
                dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)
                stanza = ivrs.get_stanza(None)
                iteration = ivrs.get_iteration(None)
                util.log(dest_c_name)
                return str(
                    ivrs.ivr_context(
                        dest_c_dict,
                        lang,
                        dest_c_name,
                        stanza,
                        iteration,
                        request,
                        env))

    # Send the operator to the next caller in the queue.
    response = VoiceResponse()
    dial = response.dial(
        timeout=3, # Connection timeout, so if the queue is empty we give up.
        action=util.function_url(request, 'outgoing_operator_dialer_status'))
    dial.queue('operator')
    return response

def outgoing_operator_operator_pre(request, env):
    """
    Return TwiML to notify and end the call if the operator queue is empty,
    otherwise return None.
    """
    util.log('outgoing_operator_pre')
    lang = request.query_params.get('lang', 'en')
    twilio_account_sid = env['TWILIO_ACCOUNT_SID']
    twilio_auth_token = env['TWILIO_AUTH_TOKEN']
    client = Client(twilio_account_sid, twilio_auth_token)
    # Is there still a caller in the queue?
    for queue in client.queues.list():
        if queue.friendly_name == operator_queue_name:
            if not queue.current_size:
                # Too late, tell the operator.
                dest_c_name = 'outgoing_operator_operator_empty'
                dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)
                stanza = ivrs.get_stanza(None)
                iteration = ivrs.get_iteration(None)
                util.log(dest_c_name)
                return str(
                    ivrs.ivr_context(
                        dest_c_dict,
                        lang,
                        dest_c_name,
                        stanza,
                        iteration,
                        request,
                        env))

def outgoing_dialtone(request, env):
    response = VoiceResponse()
    action_url = util.function_url(request, 'dial_outgoing')
    gather = response.gather(
        finish_on_key='', action=action_url, action_on_empty_result=True)
    gather.play(
        ivrs.sound_url(
            'US_dial_tone',
            'sound',
            'ops',
            env))
    return response


DESTINATIONS = {
    'friction': friction,
    'outgoing_operator_accept': outgoing_operator_accept,
    'outgoing_dialtone': outgoing_dialtone,
    'outgoing_operator_enqueue': outgoing_operator_enqueue,
    'outgoing_operator_operator_pre': outgoing_operator_operator_pre}
