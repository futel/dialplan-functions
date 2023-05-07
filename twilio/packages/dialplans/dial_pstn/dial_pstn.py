# TwiML dialer suitable as the destination for a TwiML <redirect> verb.

import re
from twilio.twiml.voice_response import VoiceResponse

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

# Return phoneNumber string normalized to E.164, if it can be.
# E.164 is +[country code][number].
def normalize_number(number):
    # XXX DigitalOcean is not letting us import the phonenumbers library?
    #     We do this klugy partial normalization instead.
    if number.startswith('+'):
        # Temporarily remove a leading +.
        number = number[1:]
    if re.match(r"/^...$/", number):
        # Allow 911, 211, etc.
        return '+' + number
    if number.startswith('011'):
        # Remove international prefix, assume the rest is NANPA + country code.
        return '+' + number[3:]
    if len(number) == 10:
        # Assume NANPA, add country code.
        return '+1' + number
    return '+' + number

# Return transformed number, if we have one.
def transform_number(phone_number):
    if phone_number in transform_numbers:
        return transform_numbers[phone_number]
    return phone_number

def filter_outgoing_number(number):
    if re.match(r"/^\+...$/", number):
        # Allow 911, 211, etc.
        return False
    if not (number.startswith('+1' + usa_code) or
            number.startswith('+1' + mexico_code)):
        # Not NANPA or Mexico. Note that Twilio might still reject
        # some NANPA, depending on settings.
        return False
        for prefix in premium_nanpa_codes:
            if number.startswith('+1' + prefix):
                return True
    return False

def dial_pstn(event, context):
    """Return TwiML to dial PSTN number with attributes from event."""
    # XXX Are we assuming that the to number is E.164?
    to_uri = event['to_uri']
    from_uri = event['from_uri']

    to_number = util.sip_to_exension(to_uri)
    to_number = normalize_number(to_number)
    to_number = transform_number(to_number)
    if filter_outgoing_number(to_number):
        # XXX notify
        #twiml.say("We're sorry, your call cannot be completed as dialed. Please check the number and try again.");
        #twiml.reject();
        return util.twiml_response('')

    # The caller ID is the SIP extension we are calling from, which we assume is E.164.
    from_extension = util.sip_to_exension(from_uri)
    caller_id = extensions[from_extension]['caller_id']

    util.log(f'caller_id: {caller_id}')
    util.log(f'to_number: {to_number}')

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        caller_id=caller_id,
        answer_on_bridge=True,
        action=util.function_url(context, 'metric_dialer_status'))
    dial.number(to_number)
    return util.twiml_response(response)
