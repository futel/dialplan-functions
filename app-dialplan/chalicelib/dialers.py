"""
Functions returning TwiML to application HTTP endpoints.
"""

from twilio.twiml.voice_response import VoiceResponse

from . import ivrs
from . import ivr_destinations
from . import metric
from . import util

sip_domain_subdomain_base = "direct-futel"
# Note that we don't use sip.us1
# https://www.twilio.com/docs/voice/api/sip-registration
sip_domain_suffix = "sip.twilio.com"
#sip_edge = "edge=umatilla"

operator_message_max = 60 * 15  # 15 minutes


def _get_sip_domain(extension, env):
    extension_map = env['extensions']
    return (sip_domain_subdomain_base +
            '-' + util.get_instance(env) +
            '.' +
            sip_domain_suffix)

def dial_extension(extension_name, request, env):
    """
    Return TwiML string to call extension.
    """
    from_user = request.from_user
    metric.publish('dial_extension', from_user, env)
    if from_user == 'hot-leet':
        # We are an incoming call, or an outgoing call from a twilio REST
        # client.
        from_number = request.from_number
    else:
        # We are an outgoing call, find out what to tell it.
        from_extension = util.sip_to_extension(from_user, env)
        from_number = from_extension['caller_id']
    return _dial_sip(extension_name, from_number, request, env)

def dial_e164_extension(request, env):
    """
    Return TwiML string to call an extension registered to our SIP Domains,
    looked up by the E.164 number in the Digits of the request.
    """
    from_user = request.from_user
    metric.publish('dial_e164_extension', from_user, env)

    # Find the extension to call, and redirect to call it.
    to_number = request.post_fields['Digits']
    to_number = util.normalize_number(to_number)
    to_extension = util.e164_to_extension(to_number, env['extensions'])
    if to_extension:
        response = VoiceResponse()
        response.redirect('/dial_extension/{}'.format(to_extension))
        return str(response)

    # It didn't match the number of one of our SIP extensions.
    response = VoiceResponse()
    response.redirect('/reject')
    return str(response)

def dial_outgoing(request, env):
    """
    Return TwiML string to dial PSTN, dial SIP URI, or play IVR,
    with attributes from request.
    """
    from_user = request.from_user
    metric.publish('dial_outgoing', from_user, env)
    from_extension = util.sip_to_extension(from_user, env)
    to_extension = util.deserialize_pstn(request)
    util.log('to_extension {}'.format(to_extension))

    if to_extension == '0':
        # Redirect to the outgoing operator context.
        response = VoiceResponse()
        response.redirect('/ivr/outgoing_operator_caller')
        return str(response)
    if to_extension == '#':
        # Redirect to the top ivr context.
        response = VoiceResponse()
        response.redirect('/ivr')
        return str(response)

    # It's a number to dial from a dialtone. Normalize, transform, filter.
    to_number = util.pstn_number(to_extension, from_extension['enable_emergency'])
    if not to_number:
        util.log('filtered pstn number {}'.format(to_extension))
        response = VoiceResponse()
        response.redirect('/reject')
        return str(response)

    # # If it's an incoming IVR number,
    # # redirect to play that IVR instead of continuing to PSTN call it.
    # if to_number == "+15034681337":
    #     response = VoiceResponse()
    #     response.redirect('/ivrs/incoming_leet')
    #     return str(response)

    # If it's the number of one of our extensions,
    # redirect to SIP call it instead of PSTN calling it.
    to_extension = util.e164_to_extension(to_number, env['extensions'])
    if to_extension:
        response = VoiceResponse()
        response.redirect('/dial_extension/{}'.format(to_extension))
        return str(response)

    # It's a PSTN number, call it.
    # We can't redirect here beucase we don't know if we got to_number from
    # Digits or not. We need to preserve Digits if we have it.
    metric.publish('dial_pstn', from_user, env)
    return str(util.dial_pstn(to_number, from_extension, request))

# This might more normally named dial_incoming_e164.
def dial_sip_e164(request, env):
    """
    Return TwiML string to call an extension registered to our SIP Domains,
    looked up by the E.164 number in the To of the request.
    """
    # Find the calling user.
    # We only expect to be taking incoming calls from external numbers, so we
    # could just normalize to "hot-leet". We don't want to metric external from
    # numbers, and that's the only reason we need a user.
    from_user = request.from_user
    metric.publish('dial_sip_e164', from_user, env)

    # Find the number being called.
    to_number = request.post_fields['To']
    to_number = util.normalize_number(to_number)

    # Find the extension to call, and redirect to call it.
    to_extension = util.e164_to_extension(to_number, env['extensions'])
    if to_extension:
        response = VoiceResponse()
        response.redirect('/dial_extension/{}'.format(to_extension))
        return str(response)

    # It didn't match the number of one of our SIP extensions.
    response = VoiceResponse()
    response.redirect('/reject')
    return str(response)

def _dial_sip(extension, from_number, request, env):
    """Return TwiML to dial a SIP client on our Twilio SIP domain."""
    sip_domain = _get_sip_domain(extension, env)
    sip_uri = f'sip:{extension}@{sip_domain}'
    util.log('sip_uri: {}'.format(sip_uri))

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        answer_on_bridge=True,
        caller_id=from_number,
        action='/ops/call_status_outgoing')
    dial.sip(sip_uri)
    return str(response)

def ivr(context_name, request, env):
    """
    Return TwiML string to play IVR context with attributes from request,
    or send the call to the Asterisk server if we can't find it.
    IVR TwiML can come from the IVR assets or the ivr_destinations module.
    """
    from_user = request.from_user
    metric.publish('ivr', from_user, env)
    # Params from twilio are in the body, params from us are in the
    # query string. We aren't supposted to combine them in a request.
    digits = request.post_fields.get('Digits')
    parent_name = request.query_params.get('parent')
    stanza = request.query_params.get('stanza')
    iteration = request.query_params.get('iteration')
    lang = request.query_params.get('lang', 'en')
    # Deserialize.
    stanza = ivrs.get_stanza(stanza)
    iteration = ivrs.get_iteration(iteration)

    util.log('context_name:{} stanza:{} digits:{}'.format(
        context_name, stanza, digits))

    # Where are we coming from?
    if not context_name:
        # We don't know where we are coming from, so we are coming from the
        # default context, presumably this is the first interaction.
        from_extension = util.sip_to_extension(from_user, env)
        context_name = from_extension['outgoing']
    c_dict = ivrs.context_dict(env['ivrs'], context_name)

    # What destination should we play?
    if digits:
        dest_c_name = ivrs.destination_context_name(digits, c_dict)
    else:
        # There wasn't a digit, the same context is our destination.
        dest_c_name = context_name

    # Get the lang and source dict for the destination to play.
    if dest_c_name is ivrs.LANG_DESTINATION:
        dest_c_dict = c_dict # Same context.
        lang = ivrs.swap_lang(lang)
    elif dest_c_name is ivrs.PARENT_DESTINATION:
        dest_c_dict = ivrs.context_dict(env['ivrs'], parent_name)
    else:
        dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)

    if not dest_c_dict:
        # We didn't find an IVR context in the context_dict.
        # If it is an IVR destination, return the output of the function.
        destination = ivr_destinations.get_destination(dest_c_name)
        if destination:
            # This is an ivr destination, so metric. We can assume this is
            # the first stanza and iteration.
            metric.publish(dest_c_name, from_user, env)
            return str(destination(request, env))
        else:
            # We don't know this context, so it's on the Asterisk server.
            to_extension = dest_c_name
            # This is an ivr destination, so metric.
            metric.publish('dial_sip_asterisk', from_user, env)
            # XXX we lose lang! Hopefully user remembers to hit *.
            return str(util.dial_sip_asterisk(dest_c_name, from_user, env))

    # We got this far, it's in the context_dict.
    if stanza is ivrs.INTRO_STANZA:
        # This is an ivr destination, so metric.
        metric.publish(dest_c_dict['name'], from_user, env)
    return str(
        ivrs.ivr_context(
            dest_c_dict, lang, context_name, stanza, iteration, request, env))

def _enqueue_operator_call(request, env):
    """
    Perform side effects for the enqueued operator call.
    Call operators with twiml for the accept menu.
    """
    from_user = request.from_user
    from_extension = util.sip_to_extension(from_user, env)
    from_number = from_extension['caller_id']
    client = env['twilio_client']

    operator_numbers = env['operator_numbers']

    # Get the TwiML to play for the operators.
    # Client.calls.create isn't a continuation, we can't give a relative URL
    # in the url argument or in twiml that we return.
    stage = util.get_instance(env)
    context = "outgoing_operator_operator"
    url = "https://{stage}.dialplans.phu73l.net/ivr/{context}".format(
        stage=stage, context=context)

    # Call each operator and play the TwiML.
    # XXX We need to set status_callback for side effects like metrics.
    for number in operator_numbers:
        call = client.calls.create(
            url=url,
            to=number,
            from_=from_number)

def outgoing_operator_dialer_status(request, env):
    """
    Perform side effects after a hopefully bridged operator call ends,
    and return TwiML for operators who stayed on the line.
    """
    from_user = request.from_user
    metric.publish('outgoing_operator_dialer_status', from_user, env)
    # call_status = request.post_fields['CallStatus']
    lang = request.query_params.get('lang', 'en')
    # Is this documented?
    dequeue_result = request.post_fields['DequeueResult']
    if dequeue_result == 'bridged':
        # The operator and caller were connected.
        # We could remind the operator to log, since the caller hung up first,
        # but the operator probably is the first to hang up usually.
        response = VoiceResponse()
        response.hangup()
        metric.publish('outgoing_operator_completed', from_user, env)
        return str(response)
    elif dequeue_result == 'queue-empty':
        # Too late, tell the operator.
        response = VoiceResponse()
        response.redirect('/ivrs/outgoing_operator_empty')
        return str(response)
    else:
        util.log("Unknown operator dequeue result {}".format(dequeue_result))

def enqueue_operator_wait(request, env):
    """
    Perform side effects and return TwiML string
    for the enqueue wait callback.
    """
    from_user = request.from_user
    metric.publish('enqueue_operator_wait', from_user, env)
    _enqueue_operator_call(request, env)
    response = VoiceResponse()
    # Play hold music until it's time to time out.
    response.play(
        # XXX This sound file is not in the ivrs structure, so it isn't checked.
        ivrs.sound_url(
            'operator',
            'sound',
            'ops',
            env))
    # After the hold music, leave the queue, which will then
    # resume the twiml after the enqueue statement.
    response.leave()
    return str(response)

def enqueue_operator_record(request, env):
    """
    Perform side effects and return TwiML string
    for the enqueue recording callback.
    """
    from_user = request.from_user
    metric.publish('enqueue_operator_record', from_user, env)
    # This is not much notification, but the recordings are discoverable.
    util.log("Operator message: ".format(request.post_fields['RecordingUrl']))
    response = VoiceResponse()
    response.hangup()
    return str(response)

def _find_operator_calls(client, extension, env):
    """
    Yield operator calls in progress for the call calling from extension.
    """
    for status in ('ringing', 'in-progress', 'queued'):
        # Use an arbitrary limit of 20 because we need something and don't
        # expect to have more simultaneous calls than that.
        calls = client.calls.list(status=status, limit=20)
        for record in calls:
            # We want to abort any calls to operators. There wasn't any way to
            # mark the calls on creation, so since we haven't stored anything,
            # we need to use call attributes to find them.
            # For an inbound SIP call, _from is the SIP URI of the caller's
            # extension, so we assume we are not inbound?
            # For outbound operator calls, _from is the e165 for the caller's
            # extension, so that's the one we're looking for.
            # XXX If the caller's extension has hot-leet as the caller id,
            # we won't find it.
            caller_extension = util.e164_to_extension(
                record._from, env['extensions'])
            if caller_extension == extension:
                # We found a call coming from extension, that must be it.
                yield record

def _is_operator_queue_empty(client):
    """Return True if operator queue is empty."""
    for queue in client.queues.list():
        if queue.friendly_name == ivr_destinations.operator_queue_name:
            if not queue.current_size:
                return True
    return False

def outgoing_operator_leave(request, env):
    """
    Perform side effects for a caller leaving the operator queue, and continue
    the caller's call.
    """
    # We resume here after the wait callback caused the user to
    # leave the queue.
    from_user = request.from_user
    metric.publish('outgoing_operator_leave', from_user, env)
    queue_result = request.post_fields['QueueResult']
    util.log('caller left queue: {}'.format(queue_result))
    lang = request.query_params.get('lang', 'en')
    client = env['twilio_client']

    # Handle side effects from caller surviving the queue wihout an operator.
    if _is_operator_queue_empty(client):
        # There is no caller in the queue. Cancel or notify all
        # operators not yet with a caller.
        # Get the TwiML to play for the operators.
        # Client.calls.create isn't a continuation,
        # we can't give a relative URL
        # in the url argument or in twiml that we return.
        stage = util.get_instance(env)
        context = 'outgoing_operator_empty'
        url = "https://{stage}.dialplans.phu73l.net/ivr/{context}".format(
            stage=stage, context=context)

        for record in _find_operator_calls(client, from_user, env):
            util.log('canceling outbound operator call')
            if record.status in ('ringing', 'queued'):
                record.update(status='canceled')
            else:
                record.update(url=url)

    # Return TwiML to continue the caller's call.
    response = VoiceResponse()
    if queue_result != 'bridged':
        # The caller was not connected to an operator.
        response.play(
            # XXX This sound file is not in the ivrs structure, so it isn't checked.
            ivrs.sound_url(
                'operators-are-currently-unavailable-please-leave-a-message-for-a-response-leave-your-voicemail-box-number',
                lang,
                'operator',
                env))
        response.record(
            action='/enqueue_operator_record',
            max_length=operator_message_max)
    return str(response)

def reject(request, env):
    """
    Return TwiML string to hang up the call.
    """
    from_user = request.from_user
    metric.publish('reject', from_user, env)
    response = VoiceResponse()
    # Is this playing a busy signal as documented?
    response.reject(reason="busy")
    return str(response)
