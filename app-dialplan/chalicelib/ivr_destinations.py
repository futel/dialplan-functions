"""
Functions reached by IVR menu choices.
"""

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse

from . import ivrs
from . import util

WAIT_FUNCTION = '/enqueue_operator_wait'
LEAVE_FUNCTION = '/outgoing_operator_leave'
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
    util.log('outgoing_operator_enqueue')
    lang = request.query_params.get('lang', 'en')
    response = VoiceResponse()
    response.enqueue(
        operator_queue_name,
        action=LEAVE_FUNCTION,
        wait_url=WAIT_FUNCTION)
    return response

def outgoing_operator_accept(request, env):
    """Return TwiML to send the call to the next caller in operator queue."""
    util.log('outgoing_operator_accept')
    lang = request.query_params.get('lang', 'en')
    # Is there still a caller in the queue?
    twilio_account_sid = env['TWILIO_ACCOUNT_SID']
    twilio_auth_token = env['TWILIO_AUTH_TOKEN']
    client = Client(twilio_account_sid, twilio_auth_token)
    for queue in client.queues.list():
        if queue.friendly_name == operator_queue_name:
            if not queue.current_size:
                # Too late, tell the operator.
                # XXX Make a helper for this.
                dest_c_name = 'outgoing_operator_empty'
                iteration = ivrs.get_iteration(None)
                util.log(dest_c_name)
                return str(
                    ivrs.ivr_context(
                        None,
                        lang,
                        dest_c_name,
                        None,
                        iteration,
                        request,
                        env))

    # The queue is not empty. Send the operator to the next caller in the queue.
    response = VoiceResponse()
    dial = response.dial(
        timeout=3, # Connection timeout, so if the queue is empty we give up.
        action='/outgoing_operator_dialer_status')
    dial.queue('operator')
    return response

def outgoing_operator_pre(request, env):
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
                # XXX Make a helper for this.
                dest_c_name = 'outgoing_operator_empty'
                iteration = ivrs.get_iteration(None)
                util.log(dest_c_name)
                return str(
                    ivrs.ivr_context(
                        None,
                        lang,
                        dest_c_name,
                        None,
                        iteration,
                        request,
                        env))

def _dialtone(destination, request, env):
    """Return TwiML for a dialtone sending input to destination."""
    response = VoiceResponse()
    action_url = util.function_url(request, destination)
    gather = response.gather(
        finish_on_key='', action=action_url, action_on_empty_result=False)
    gather.play(
        # XXX This sound file is not in the ivrs structure, so it isn't checked.
        ivrs.sound_url(
            'US_dial_tone',
            'sound',
            'ops',
            env))
    response.hangup()           # We should fast busy instead.
    return response

def outgoing_dialtone_pre(request, env):
    """Return TwiML for a dialtone for outgoing calls."""
    return _dialtone('dial_outgoing', request, env)

def internal_dialtone(request, env):
    """Return TwiML for a dialtone for internal calls."""
    return _dialtone('dial_e164_extension', request, env)

def call_911_911(request, env):
    """Return TwiML to call 911."""
    # This is an outgoing call from a sip client.
    from_user = util.sip_to_user(request.post_fields['From'])
    from_extension = util.sip_to_extension(from_user, env)
    return util.dial_pstn("+1911", from_extension, request)

def call_911_9_bounce(request, env):
    """
    If we can't make an emergency call, return a hangup response.
    Otherwise, return None.
    """
    # This is an outgoing call from a sip client.
    from_user = util.sip_to_user(request.post_fields['From'])
    from_extension = util.sip_to_extension(from_user, env)
    if not from_extension['enable_emergency']:
        response = VoiceResponse()
        response.hangup()
        return response
    return None

def dial_nanpa(nanpa):
    """Return a function to return TwiML to dial NANPA number."""
    e164 = "+1" + nanpa
    def curried(request, env):
        """Return twiml to dial the curried e164 number."""
        # This is an outgoing call from a sip client.
        from_user = util.sip_to_user(request.post_fields['From'])
        from_extension = util.sip_to_extension(from_user, env)
        return util.dial_pstn(e164, from_extension, request)
    return curried

def dial_sisyphus(request, env):
    """Return TwiML to dial Sisyphus."""
    return dial_nanpa(env['nanpa_sisyphus'])(request, env)

DESTINATIONS = {
    'call_911_911': call_911_911,
    'call_911_9_bounce': call_911_9_bounce,
    'dial_3138884044': dial_nanpa("3138884044"),
    'dial_5038234120': dial_nanpa("5038234120"),
    'dial_8003900934': dial_nanpa("8003900934"),
    'dial_8336287999': dial_nanpa("8336287999"),
    'dial_8443876962': dial_nanpa("8443876962"),
    'dial_sisyphus': dial_sisyphus,
    'friction': friction,
    'internal_dialtone': internal_dialtone,
    'outgoing_operator_accept': outgoing_operator_accept,
    'outgoing_dialtone_pre': outgoing_dialtone_pre,
    'outgoing_operator_enqueue': outgoing_operator_enqueue,
    'outgoing_operator_pre': outgoing_operator_pre}
