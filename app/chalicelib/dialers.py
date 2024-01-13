"""
Functions returning TwiML to application HTTP endpoints.
"""

from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client

from . import ivrs
from . import ivr_destinations
from . import metric
from . import sns_client
from . import util

sip_domain_subdomain_base_emergency = "direct-futel";
sip_domain_subdomain_base_non_emergency = "direct-futel-nonemergency";
# Note that we don't use sip.us1
# https://www.twilio.com/docs/voice/api/sip-registration
sip_domain_suffix = "sip.twilio.com";


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

def _request_to_metric_events(request, env):
    """Return sequence of metric event names from request."""
    from_uri = request.post_fields['From']
    dial_call_status = request.post_fields['DialCallStatus']

    endpoint = metric.request_to_endpoint(request, env)
    extension = util.sip_to_extension(from_uri)
    if extension:
        # Outgoing from Twilio SIP Domain,
        # from_uri is SIP URI to extension.
        dial_event = "outgoing_call"
        dial_status_event_base = "outgoing_dialstatus_"
    else:
        # Incoming to Twilio phone number.
        dial_event = "incoming_call"
        dial_status_event_base = "incoming_dialstatus_"

    dial_status_event = dial_status_event_base + dial_call_status + '_' + endpoint
    return (dial_event, dial_status_event)

def dial_outgoing(request, env):
    """
    Return TwiML string to dial PSTN, dial SIP URI, or play IVR,
    with attributes from request.
    """
    metric.publish('dial_outgoing', request, env)
    (to_extension, from_uri) = util.deserialize_pstn(request)
    from_uri = request.post_fields['From']
    from_extension = util.sip_to_extension(from_uri)
    from_extension = env['extensions'][from_extension]
    util.log('to_extension {}'.format(to_extension))
    if to_extension == '0':
        # Return twiml for the outgoing operator context.
        # This is an ivr destination, so metric.
        dest_c_name = 'outgoing_operator_caller'
        metric.publish(dest_c_name, request, env)
        dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)
        stanza = ivrs.get_stanza(None)
        iteration = ivrs.get_iteration(None)
        response = ivrs.ivr_context(
            dest_c_dict,
            'en',                   # XXX Should get the real lang!
            dest_c_name,
            stanza,
            iteration,
            request,
            env)
        return str(response)
    if to_extension == '#':
        if from_extension['local_outgoing']:
            # ivr() is also routed directly, so it mareshals
            # the response for flask. We should just
            # redirect, this is hit only once per call.
            return ivr(request, env)
        # The top menu is on the asterisk.
        metric.publish('dial_sip_asterisk', request, env)
        return str(util.dial_sip_asterisk(to_extension, request, env))
    # It's a PSTN number.
    number = util.pstn_number(to_extension, from_extension['enable_emergency'])
    if not number:
        util.log('filtered pstn number {}'.format(to_extension))
        metric.publish('reject', request, env)
        return str(util.reject(request, env))
    metric.publish('dial_pstn', request, env)
    return str(util.dial_pstn(to_extension, from_uri, request, env))

def dial_sip_e164(request, env):
    """
    Return TwiML string to call an extension registered to our SIP Domains,
    looked up by the given E.164 number.
    """
    metric.publish('dial_sip_e164', request, env)
    # XXX might be in Digits? How did we do this w/ ivr gather?
    #(to_extension, from_uri) = util.deserialize_pstn(request)
    # XXX that was sip_to_extension, we need to normalize, etc
    to_number = request.post_fields['To']
    from_number = request.post_fields['From']
    to_number = util.normalize_number(to_number)
    to_extension = util.e164_to_extension(to_number, env['extensions'])
    if not to_extension:
        util.log("Could not find extension for E.164 number")
        metric.publish('reject', request, env)
        return str(util.reject(request, env))
    return _dial_sip(to_extension, from_number, request, env)

def _dial_sip(extension, from_number, request, env):
    """Return TwiML to dial a SIP extension on our Twilio SIP domain.."""
    sip_domain = _get_sip_domain(extension, env['extensions'], request)
    sip_uri = f'sip:{extension}@{sip_domain};'
    util.log('sip_uri: {}'.format(sip_uri))

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        answer_on_bridge=True,
        caller_id=from_number,
        action=util.function_url(request, 'metric_dialer_status'))
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
        from_extension = util.sip_to_extension(from_uri)
        from_extension = env['extensions'][from_extension]
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

def metric_dialer_status(request, env):
    """
    Metric the dial status callback attributes from request,
    and return TwiML string.
    """
    # Perform the side effects.
    metric.publish('metric_dialer_status', request, env)
    # May want to log ErrorCode ErrorMessage Direction post fields.
    for event_name in _request_to_metric_events(request, env):
        metric.publish(event_name, request, env)

    # Return TwiML.
    response = VoiceResponse()
    if request.post_fields['DialCallStatus'] == 'failed':
        return str(util.reject(request, env))
    if request.post_fields['DialCallStatus'] == 'busy':
        return str(util.reject(request, env, reason='busy'))
    if request.post_fields['DialCallStatus'] == 'no-answer':
        # This could be no pickup or not registered.
        # We should care about not registered, metric something,
        # it would be nice to fast busy also.
        # The context should have this for not registered:
        # ErrorCode "32009"
        # ErrorMessage
        # "Your TwiML tried to Dial a Twilio SIP Registered User that is not currently registered"
        return str(util.reject(request, env, reason='busy'))
    # If the first interation on handset pickup is a local menu, we want to return to that.
    # If the first interation is a SIP call to a remote menu, we want to SIP it again if that
    # call hung up due to a user hitting the back key from the top, otherwise we want to end.
    # If the first interation is a dialtone, we want to end.
    response.hangup()
    return str(response)

def _enqueue_operator_call(request, env):
    """Call operators with twiml for the accept menu."""
    from_uri = request.post_fields['From']
    from_extension = util.sip_to_extension(from_uri)
    from_extension = env['extensions'][from_extension]
    from_number = from_extension['caller_id']

    twilio_account_sid = env['TWILIO_ACCOUNT_SID']
    twilio_auth_token = env['TWILIO_AUTH_TOKEN']
    client = Client(twilio_account_sid, twilio_auth_token)

    operator_numbers = env['operator_numbers']

    # Get the TwiML to play for the operators.
    dest_c_name = 'outgoing_operator_operator'
    dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)
    stanza = ivrs.get_stanza(None)
    iteration = ivrs.get_iteration(None)
    # We calculate pre_callable now, when we render the twiml, so if the
    # caller hangs up before operator pickup, the operator still gets a menu.
    # This twiml could instead redirect to outgoing_operator_operator?
    response = ivrs.ivr_context(
        dest_c_dict,
        'en',                   # XXX Should get the real lang!
        dest_c_name,
        stanza,
        iteration,
        request,
        env)

    # Call each operator and play the TwiML.
    for number in operator_numbers:
        call = client.calls.create(
            twiml=str(response),
            to=number,
            from_=from_number)

def outgoing_operator_dialer_status(request, env):
    """
    Metric and return a TwiML string for operators who stayed on the line.
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
        dest_c_name = 'outgoing_operator_empty'
        dest_c_dict = ivrs.context_dict(env['ivrs'], dest_c_name)
        stanza = ivrs.get_stanza(None)
        iteration = ivrs.get_iteration(None)
        # This is an ivr destination, so metric.
        metric.publish(dest_c_name, request, env)
        return str(
            ivrs.ivr_context(
                dest_c_dict,
                lang,
                dest_c_name,
                stanza,
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
    response.play(
        'http://com.twilio.sounds.music.s3.amazonaws.com/MARKOVICHAMP-Borghestral.mp3')
    return str(response)
