# TwiML dialer suitable as the destination for a TwiML <redirect> verb.

from twilio.twiml.voice_response import VoiceResponse

import util

sip_domain_subdomain_base_emergency = "direct-futel";
sip_domain_subdomain_base_non_emergency = "direct-futel-nonemergency";
sip_domain_suffix = "sip.us1.twilio.com";

extensions = util.get_extensions()

def get_sip_domain(extension, extension_map):
    if extension_map[extension]['enable_emergency']:
        sip_domain_subdomain_base = sip_domain_subdomain_base_emergency
    else:
        sip_domain_subdomain_base = sip_domain_subdomain_base_non_emergency
    return sip_domain_subdomain_base + '-' + util.get_instance() + '.' + sip_domain_suffix

def dial_sip_e164(event, context):
    """Return TwiML to dial SIP URI with attributes from event."""
    util.log('dial_sip_e164')
    to_number = event['to_number']
    from_number = event['from_number']

    to_number = util.normalize_number(to_number)
    to_extension = util.e164_to_extension(to_number, extensions)
    if not to_extension:
        util.log("Could not find extension for E.164 number")
        response.redirect(util.function_url(context, 'reject'))
        return util.twiml_response(response)
    sip_domain = get_sip_domain(to_extension, extensions)
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
