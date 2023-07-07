"""
Return TwiML to dial a PSTN number.
"""

from twilio.twiml.voice_response import VoiceResponse

import metric
import util

extensions = util.get_extensions()

# Map of phone numbers to transform.
transform_numbers = {'+211': '+18666986155'}
# Allowed country codes.
usa_code = '1';
mexico_code = '52';
# Area codes of expensive NANPA numbers.
premium_nanpa_codes = [
    '900',
    '976',
    '242',
    '246',
    '264',
    '268',
    '284',
    '345',
    '441',
    '473',
    '649',
    '664',
    '721',
    '758',
    '767',
    '784',
    '809',
    '829',
    '849',
    '868',
    '869',
    '876']

# Return transformed number, if we have one.
def transform_number(phone_number):
    if phone_number in transform_numbers:
        return transform_numbers[phone_number]
    return phone_number

def filter_outgoing_number(number):
    """Return True if number should be filtered."""
    if len(number) == 4:
        # Allow 911, 211, etc.
        return False
    if not (number.startswith('+' + usa_code) or
            number.startswith('+' + mexico_code)):
        # Not NANPA or Mexico.
        return True
    # Should we validate US length here?
    # Can we validate Mexico length here?
    # Check for expensive NANPA numbers.
    # Note that Twilio might still reject some NANPA,
    # depending on settings.
    for prefix in premium_nanpa_codes:
        if number.startswith('+1' + prefix):
            return True
    return False

def dial_pstn(event, context, env):
    """Return TwiML to dial PSTN number with attributes from event."""
    metric.publish('dial_pstn', event, env)
    to_uri = event['to_uri']
    from_uri = event['from_uri']
    response = VoiceResponse()

    to_number = util.sip_to_extension(to_uri)
    to_number = util.normalize_number(to_number)
    to_number = transform_number(to_number)
    util.log(f'to_number: {to_number}')
    if filter_outgoing_number(to_number):
        util.log(f'filtered to_number: {to_number}')
        response.redirect(util.function_url(context, 'reject'))
        return util.twiml_response(response)

    from_extension = util.sip_to_extension(from_uri)
    caller_id = extensions[from_extension]['caller_id']

    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        caller_id=caller_id,
        answer_on_bridge=True,
        action=util.function_url(context, 'metric_dialer_status'))
    dial.number(to_number)
    metric.publish('dialing', event, env) # We passed the filter.
    return util.twiml_response(response)
