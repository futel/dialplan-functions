from twilio.twiml.voice_response import VoiceResponse

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
    """Return sequence of sns_client metric events from DO request."""
    to_uri = request.post_fields['To']
    from_uri = request.post_fields['From']
    dial_call_status = request.post_fields['DialCallStatus']
    dial_event = None

    endpoint = metric.request_to_endpoint(request)

    extension = util.sip_to_extension(from_uri)
    if extension:
        # Outgoing from Twilio SIP Domain,
        # from_uri is SIP URI to extension.
        dial_user_event = "outgoing_call"
        dial_status_user_event_base = "outgoing_dialstatus_"
    else:
        # Incoming to Twilio phone number,
        # to_uri is E.164 of caller.
        dial_user_event = "incoming_call"
        dial_status_user_event_base = "incoming_dialstatus_"

    dial_status_user_event = dial_status_user_event_base + dial_call_status + '_' + endpoint;
    dial_event = {
        'endpoint': endpoint,
        'user_event': dial_user_event};
    dial_status_event = {
        'endpoint': endpoint,
        'user_event': dial_status_user_event};
    return (dial_event, dial_status_event)

# XXX no longer a dialer?
def reject(request):
    """Return TwiML reject call."""
    metric.publish('reject', request)
    response = VoiceResponse()
    response.say(
        "We're sorry, your call cannot be completed as dialed. "
        "Please check the number and try again.");
    response.reject()
    return util.twiml_response(response)

def dial_outgoing(request):
    """Return TwiML to dial SIP URI with attributes from request."""
    metric.publish('dial_outgoing', request)
    to_uri = request.post_fields['To']
    #from_uri = request.post_fields['From']
    #from_extension = util.sip_to_extension(from_uri)
    to_extension = util.sip_to_extension(to_uri)
    extensions = util.get_extensions()
    if to_extension == '0':
        response = util.dial_sip(request)
        return util.twiml_response(response)
    elif to_extension == '#':
        #if extensions[from_extension]['local_outgoing']:
        #    function = 'ivr'
        response = util.dial_sip(request)
        return util.twiml_response(response)
    response = util.dial_pstn(request)
    return util.twiml_response(response)

def dial_sip_e164(request):
    """
    Return TwiML to call an extension registered to our Twilio SIP Domains, looked up by
    the given E.164 number.
    """
    metric.publish('dial_sip_e164', request)
    to_number = request.post_fields['To']
    from_number = request.post_fields['From']
    to_number = util.normalize_number(to_number)
    extensions = util.get_extensions()
    to_extension = util.e164_to_extension(to_number, extensions)
    if not to_extension:
        util.log("Could not find extension for E.164 number")
        response = util.reject(request)
        return util.twiml_response(response)
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
    return util.twiml_response(response)

def metric_dialer_status(request):
    """
    Metric the dial status callback attributes from request,
    and return TwiML.
    """
    # Perform the side effects.
    metric.publish('metric_dialer_status', request)
    for e in request_to_metric_events(request):
        sns_client.publish(e['endpoint'], e['user_event'], request)

    # Return TwiML.
    response = VoiceResponse()
    if request.post_fields['DialCallStatus'] == 'failed':
        # XXX just return reject(request)
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
    return util.twiml_response(response)
