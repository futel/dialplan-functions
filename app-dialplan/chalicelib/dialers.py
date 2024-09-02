"""
Functions returning TwiML to application HTTP endpoints.
"""

from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client

from . import ivrs
from . import ivr_destinations
from . import metric
from . import util

sip_domain_subdomain_base_emergency = "direct-futel"
sip_domain_subdomain_base_non_emergency = "direct-futel-nonemergency"
# Note that we don't use sip.us1
# https://www.twilio.com/docs/voice/api/sip-registration
sip_domain_suffix = "sip.twilio.com"
#sip_edge = "edge=umatilla"

operator_message_max = 60 * 15  # 15 minutes


def _get_sip_domain(extension, extension_map, request):
    if extension_map[extension]['enable_emergency']:
        sip_domain_subdomain_base = sip_domain_subdomain_base_emergency
    else:
        sip_domain_subdomain_base = (
            sip_domain_subdomain_base_non_emergency)
    return (sip_domain_subdomain_base +
            '-' + util.get_instance(request) +
            '.' +
            sip_domain_suffix)

def _call_status(request):
    """Return the call status indicated by the request."""
    call_status = request.post_fields.get('DialCallStatus')
    if call_status:
        # Status callack from twilio pv running twiml on call create.
        return call_status
    # Status callack from twilio REST client on call create.
    return request.post_fields.get('CallStatus')

def dial_outgoing(request, env):
    """
    Return TwiML string to dial PSTN, dial SIP URI, or play IVR,
    with attributes from request.
    """
    metric.publish('dial_outgoing', request, env)
    to_extension = util.deserialize_pstn(request)
    from_uri = request.post_fields['From']
    from_extension = util.sip_to_extension(from_uri, env)
    util.log('to_extension {}'.format(to_extension))
    if to_extension == '0':
        # Return twiml for the outgoing operator context.
        # This is an ivr destination, so metric.
        # XXX Make a helper for this.
        dest_c_name = 'outgoing_operator_caller'
        metric.publish(dest_c_name, request, env)
        dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)
        stanza = ivrs.get_stanza(None)
        iteration = ivrs.get_iteration(None)
        response = ivrs.ivr_context(
            dest_c_dict,
            'en',                   # XXX Should get the real lang!
            dest_c_name,
            None,
            iteration,
            request,
            env)
        return str(response)
    if to_extension == '#':
        if from_extension['local_outgoing']:
            # ivr() is also routed directly, so it marshals
            # the response for flask.
            return ivr(request, env)
        # The top menu is on the asterisk.
        metric.publish('dial_sip_asterisk', request, env)
        return str(util.dial_sip_asterisk(to_extension, request, env))

    # It's an E.164 number, normalize, filter, transform.
    to_number = util.pstn_number(to_extension, from_extension['enable_emergency'])
    if not to_number:
        util.log('filtered pstn number {}'.format(to_extension))
        metric.publish('reject', request, env)
        return str(util.reject(request, env))

    # If it's the number of one of our extensions, SIP call it.
    to_extension = util.e164_to_extension(to_number, env['extensions'])
    if to_extension:
        metric.publish('dial_sip', request, env)
        from_number = from_extension['caller_id']
        return _dial_sip(to_extension, from_number, request, env)

    # It's a PSTN number, call it.
    metric.publish('dial_pstn', request, env)
    return str(util.dial_pstn(to_number, from_extension, request, env))

def dial_sip_e164(request, env):
    """
    Return TwiML string to call an extension registered to our SIP Domains,
    looked up by the given E.164 number.
    """
    metric.publish('dial_sip_e164', request, env)
    to_number = request.post_fields['To']
    from_uri = request.post_fields['From']
    to_number = util.pstn_number(to_number, enable_emergency=False)

    to_extension = util.e164_to_extension(to_number, env['extensions'])
    if to_extension:
        return _dial_sip(to_extension, from_uri, request, env)

    util.log("Could not find extension for E.164 number")
    metric.publish('reject', request, env)
    return str(util.reject(request, env))

def _dial_sip(extension, from_number, request, env):
    """Return TwiML to dial a SIP client on our Twilio SIP domain."""
    sip_domain = _get_sip_domain(extension, env['extensions'], request)
    #sip_uri = f'sip:{extension}@{sip_domain};{sip_edge}'
    sip_uri = f'sip:{extension}@{sip_domain}'
    util.log('sip_uri: {}'.format(sip_uri))

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        answer_on_bridge=True,
        caller_id=from_number,
        action=util.function_url(request, 'ops/call_status_sip'))
    dial.sip(sip_uri)
    return str(response)

def ivr(request, env):
    """
    Return TwiML string to play IVR context with attributes from request,
    or send the call to the Asterisk server if we can't find it.
    IVR TwiML can come from the IVR assets or the ivr_destinations module.
    """
    metric.publish('ivr', request, env)
    # Params from twilio are in the body, params from us are in the
    # query string. We aren't supposted to combine them.
    from_uri = request.post_fields['From']
    #to_uri = request.post_fields['To']
    digits = request.post_fields.get('Digits')
    c_name = request.query_params.get('context')
    parent_name = request.query_params.get('parent')
    stanza = request.query_params.get('stanza')
    iteration = request.query_params.get('iteration')
    lang = request.query_params.get('lang', 'en')
    # Deserialize.
    stanza = ivrs.get_stanza(stanza)
    iteration = ivrs.get_iteration(iteration)

    util.log('c_name:{} stanza:{} digits:{}'.format(c_name, stanza, digits))
    # Find the destination ivr context dict.
    if not c_name:
        # Presumably this is the first interaction, go to the
        # default context.
        from_extension = util.sip_to_extension(from_uri, env)
        c_name = from_extension['outgoing']
        dest_c_dict = ivrs.context_dict(env['ivrs'], c_name)
    else:
        c_dict = ivrs.context_dict(env['ivrs'], c_name)
        if not digits:
            # There wasn't a digit, the same context is our destination.
            dest_c_name = c_name
            dest_c_dict = c_dict
        else:
            dest_c_name = ivrs.destination_context_name(digits, c_dict)
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
                metric.publish(dest_c_name, request, env)
                return str(destination(request, env))
            else:
                # We don't know this context, so it's on the Asterisk server.
                to_extension = dest_c_name
                # This is an ivr destination, so metric.
                metric.publish('dial_sip_asterisk', request, env)
                # XXX we lose lang! Hopefully user remembers to hit *.
                return str(util.dial_sip_asterisk(dest_c_name, request, env))

    # We got this far, it's in the context_dict.
    if stanza is ivrs.INTRO_STANZA:
        # This is an ivr destination, so metric.
        metric.publish(dest_c_dict['name'], request, env)
    return str(
        ivrs.ivr_context(
            dest_c_dict, lang, c_name, stanza, iteration, request, env))

def _enqueue_operator_call(request, env):
    """
    Perform side effects for the enqueued operator call.
    Call operators with twiml for the accept menu.
    """
    from_uri = request.post_fields['From']
    from_extension = util.sip_to_extension(from_uri, env)
    from_number = from_extension['caller_id']

    twilio_account_sid = env['TWILIO_ACCOUNT_SID']
    twilio_auth_token = env['TWILIO_AUTH_TOKEN']
    client = Client(twilio_account_sid, twilio_auth_token)

    operator_numbers = env['operator_numbers']

    # Get the TwiML to play for the operators.
    # XXX Make a helper for this.
    dest_c_name = 'outgoing_operator_operator'
    dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)
    iteration = ivrs.get_iteration(None)
    # We calculate pre_callable now, when we render the twiml, so if the
    # caller hangs up before operator pickup, the operator still gets a menu.
    # This twiml could instead redirect to outgoing_operator_operator?
    response = ivrs.ivr_context(
        dest_c_dict,
        'en',                   # XXX Should get the real lang!
        dest_c_name,
        None,
        iteration,
        request,
        env)

    # Call each operator and play the TwiML.
    # XXX We need to set status_callback for side effects like metrics.
    for number in operator_numbers:
        call = client.calls.create(
            twiml=str(response),
            to=number,
            from_=from_number)

def outgoing_operator_dialer_status(request, env):
    """
    Perform side effects after a hopefully bridged operator call ends,
    and return TwiML for operators who stayed on the line.
    """
    metric.publish('outgoing_operator_dialer_status', request, env)
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
        metric.publish('outgoing_operator_completed', request, env)
        return str(response)
    elif dequeue_result == 'queue-empty':
        # Too late, tell the operator.
        # XXX Make a helper for this.
        dest_c_name = 'outgoing_operator_empty'
        dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)
        iteration = ivrs.get_iteration(None)
        # This is an ivr destination, so metric.
        metric.publish(dest_c_name, request, env)
        return str(
            ivrs.ivr_context(
                dest_c_dict,
                lang,
                dest_c_name,
                None,
                iteration,
                request,
                env))
    else:
        util.log("Unknown operator dequeue result {}".format(dequeue_result))

def enqueue_operator_wait(request, env):
    """
    Perform side effects and return TwiML string
    for the enqueue wait callback.
    """
    metric.publish('enqueue_operator_wait', request, env)
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
    metric.publish('enqueue_operator_record', request, env)
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
            # extension. For outbound operator calls, it is the e165 for the
            # caller's extension.
            caller_extension = util.e164_to_extension(
                record._from, env['extensions'])
            if caller_extension == extension:
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
    metric.publish('outgoing_operator_leave', request, env)
    queue_result = request.post_fields['QueueResult']
    util.log('caller left queue: {}'.format(queue_result))
    from_uri = request.post_fields['From']
    from_user = util.sip_to_user(from_uri)
    lang = request.query_params.get('lang', 'en')
    twilio_account_sid = env['TWILIO_ACCOUNT_SID']
    twilio_auth_token = env['TWILIO_AUTH_TOKEN']
    client = Client(twilio_account_sid, twilio_auth_token)
    if _is_operator_queue_empty(client):
        # There is no caller in the queue. Cancel or notify all
        # operators not yet with a caller.
        for record in _find_operator_calls(client, from_user, env):
            util.log('canceling outbound operator call')
            if record.status in ('ringing', 'queued'):
                record.update(status='canceled')
            else:
                # Notify the operator that they are too late.
                # XXX Make a helper for this.
                dest_c_name = 'outgoing_operator_empty'
                dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)
                iteration = ivrs.get_iteration(None)
                util.log(dest_c_name)
                response = str(
                    ivrs.ivr_context(
                        None,
                        lang,
                        dest_c_name,
                        None,
                        iteration,
                        request,
                        env))
                record.update(twiml=response)
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
            action=util.function_url(request, 'enqueue_operator_record'),
            max_length=operator_message_max)
    return str(response)
