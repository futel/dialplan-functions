"""
Return TwiML to call an extension registered to our Twilio SIP Domains, looked up by
the given E.164 number.
"""

from twilio.twiml.voice_response import VoiceResponse

import metric
import util

sip_domain_subdomain_base_emergency = "direct-futel";
sip_domain_subdomain_base_non_emergency = "direct-futel-nonemergency";
# Note that we don't use sip.us1
# https://www.twilio.com/docs/voice/api/sip-registration
sip_domain_suffix = "sip.twilio.com";

extensions = util.get_extensions()

def get_sip_domain(extension, extension_map, env):
    if extension_map[extension]['enable_emergency']:
        sip_domain_subdomain_base = sip_domain_subdomain_base_emergency
    else:
        sip_domain_subdomain_base = sip_domain_subdomain_base_non_emergency
    return sip_domain_subdomain_base + '-' + util.get_instance(env) + '.' + sip_domain_suffix

def dial_sip_e164(event, context, env):
    """Return TwiML to dial SIP URI with attributes from event."""
    event = util.twilio_event_to_event(event)
    metric.publish('dial_sip_e164', event, env)
    from_number = event['from_uri']
    to_number = event['to_uri']

    to_number = util.normalize_number(to_number)
    to_extension = util.e164_to_extension(to_number, extensions)
    if not to_extension:
        util.log("Could not find extension for E.164 number")
        response.redirect(util.function_url(context, 'reject'))
        return util.twiml_response(response)
    sip_domain = get_sip_domain(to_extension, extensions, env)
    util.log(f'to_extension: {to_extension}')
    util.log(f'from_number: {from_number}')
    util.log(f'sip_domain: {sip_domain}')

    sip_uri = f'sip:{to_extension}@{sip_domain};'

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        answer_on_bridge=True,
        caller_id=from_number,
        action=util.function_url(context, 'metric_dialer_status'))
    dial.sip(sip_uri)
    return util.twiml_response(response)
