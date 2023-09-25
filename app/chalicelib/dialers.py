from twilio.twiml.voice_response import VoiceResponse

from . import ivrs
from . import metric
from . import sns_client
from . import util

sip_domain_subdomain_base_emergency = "direct-futel";
sip_domain_subdomain_base_non_emergency = "direct-futel-nonemergency";
# Note that we don't use sip.us1
# https://www.twilio.com/docs/voice/api/sip-registration
sip_domain_suffix = "sip.twilio.com";

def get_sip_domain(extension, extension_map, request):
    if extension_map[extension]['enable_emergency']:
        sip_domain_subdomain_base = sip_domain_subdomain_base_emergency
    else:
        sip_domain_subdomain_base = sip_domain_subdomain_base_non_emergency
    return sip_domain_subdomain_base + '-' + util.get_instance(request) + '.' + sip_domain_suffix

def request_to_metric_events(request):
    """Return sequence of metric event names from request."""
    from_uri = request.post_fields['From']
    dial_call_status = request.post_fields['DialCallStatus']

    endpoint = metric.request_to_endpoint(request)
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
    Return TwiML to dial SIP URI, or play IVR,
    with attributes from request.
    """
    metric.publish('dial_outgoing', request, env)
    to_uri = request.post_fields['To']
    from_uri = request.post_fields['From']
    from_extension = util.sip_to_extension(from_uri)
    from_extension = util.get_extensions()[from_extension]
    to_extension = util.sip_to_extension(to_uri)
    if to_extension == '0':
        # XXX Could convert to 'operator' here and send that,
        #     avoid an uwieldy dup if in dial_sip.
        return util.dial_sip(request, env)
    if to_extension == '#':
        if from_extension['local_outgoing']:
            # ivr() is also routed directly, so it marshals
            # the response for flask. We could just
            # redirect, this is hit only once per call.
            return ivr(request, env)
        return util.dial_sip(request, env)
    return util.dial_pstn(request, env)

def dial_sip_e164(request, env):
    """
    Return TwiML to call an extension registered to our Twilio SIP Domains, looked up by
    the given E.164 number.
    """
    metric.publish('dial_sip_e164', request, env)
    to_number = request.post_fields['To']
    from_number = request.post_fields['From']
    to_number = util.normalize_number(to_number)
    extensions = util.get_extensions()
    to_extension = util.e164_to_extension(to_number, extensions)
    if not to_extension:
        util.log("Could not find extension for E.164 number")
        return util.reject(request)
    sip_domain = get_sip_domain(to_extension, extensions, request)
    util.log(f'to_extension: {to_extension}')
    util.log(f'from_number: {from_number}')
    util.log(f'sip_domain: {sip_domain}')

    sip_uri = f'sip:{to_extension}@{sip_domain};'

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        answer_on_bridge=True,
        caller_id=from_number,
        action=util.function_url(request, 'metric_dialer_status'))
    dial.sip(sip_uri)
    return response

def ivr(request, env):
    """Return TwiML to play IVR context with attributes from request."""
    metric.publish('ivr', request, env)
    from_uri = request.post_fields['From']
    #to_uri = request.post_fields['To']
    digits = request.post_fields.get('Digits')
    c_name = request.post_fields.get('context')
    parent_name = request.post_fields.get('parent') # Should use a session.
    lang = request.post_fields.get('lang', 'en')

    # Find the destination ivr context dict.
    from_extension = util.sip_to_extension(from_uri)
    extensions = util.get_extensions()
    ivr_d = util.get_ivrs()
    if not c_name:
        # Presumably this is the first interaction.
        c_name = extensions[from_extension]['outgoing']
        dest_c_dict = ivrs.context_dict(ivr_d, c_name)
    else:
        # User entered a digit.
        c_dict = ivrs.context_dict(ivr_d, c_name)
        dest_c_name = ivrs.destination_context_name(digits, c_dict)
        if dest_c_name == ivrs.LANG_DESTINATION:
            dest_c_dict = c_dict # Same context.
            lang = ivrs.swap_lang(lang)
        elif dest_c_name == ivrs.PARENT_DESTINATION:
            dest_c_dict = ivrs.context_dict(ivr_d, parent_name)
        else:
            dest_c_dict = ivrs.context_dict(ivr_d, c_name)
        if not dest_c_dict:
            # We don't know this context, so it's on the Asterisk server.
            to_extension = dest_c_name
            # XXX we lose lang! Hopefully user remembers to hit *.
            return util.dial_sip(request, env)

    return ivrs.ivr_context(dest_c_dict, lang, c_name, request, env)

def metric_dialer_status(request, env):
    """
    Metric the dial status callback attributes from request,
    and return TwiML.
    """
    # Perform the side effects.
    metric.publish('metric_dialer_status', request, env)
    for event_name in request_to_metric_events(request):
        metric.publish(event_name, request, env)

    # Return TwiML.
    response = VoiceResponse()
    if request.post_fields['DialCallStatus'] == 'failed':
        # XXX just util.reject(request)
        response.say(
            "We're sorry, your call cannot be completed as dialed. "
            "Please try again later.")
    if request.post_fields['DialCallStatus'] == 'busy':
        response.reject(reason='busy')
    if request.post_fields['DialCallStatus'] == 'no-answer':
        # This could be no pickup or not registered.
        # We should care about not registered, metric something,
        # it would be nice to fast busy also.
        # The context should have this for not registered:
        # ErrorCode "32009"
        # ErrorMessage "Your TwiML tried to Dial a Twilio SIP Registered User that is not currently registered"
        response.reject(reason='busy')
    else:
        # If the first interation on handset pickup is a local menu, we want to return to that.
        # If the first interation is a SIP call to a remote menu, we want to SIP it again if that
        # call hung up due to a user hitting the back key from the top, otherwise we want to end.
        # If the first interation is a dialtone, we want to end.
        response.hangup()
    return response
