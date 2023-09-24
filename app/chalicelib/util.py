import dotenv
from chalice import Response
import json
import os
from twilio.twiml.voice_response import VoiceResponse
from urllib import parse

# XXX put metric calls back in dialer
from . import metric

dotenv.load_dotenv(os.path.join(
    os.path.dirname(__file__), 'environment', '.env'))

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

def log(msg):
    print(msg)

def get_env():
    return {
        'ASSET_HOST': os.environ['ASSET_HOST'],
        'AWS_TOPIC_ARN': os.environ['AWS_TOPIC_ARN']}

def get_extensions():
    """Return extensions asset object."""
    filename = os.path.join(
        os.path.dirname(__file__), 'assets', 'extensions.json')
    with open(filename) as f:
        return json.load(f)

def get_instance(request):
    """Return the deployment environment name eg 'prod', 'stage', 'dev'."""
    return request.context['domainPrefix']

def function_url(request, function_name):
    """
    Return the URL for another function served by the same host.
    """
    # All functions HTTPS, top-level in the path on the same host.
    #if params:
    #    # XXX we are putting URL arguments on a POST that may have body parameters.
    #    params = parse.urlencode(params)
    #    url += '?' + params
    return 'https://' + request.headers['host'] + '/' + function_name

#sip:test@direct-futel-nonemergency-stage.sip.twilio.com
def sip_to_extension(sip_uri):
    """Return the extension from a SIP URI, or None."""
    try:
        extension = sip_uri.split('@')[0].split(':')[1]
        extension = parse.unquote(extension)
        return extension
    except IndexError:
        return None

def e164_to_extension(e164, extension_map):
    """Return an extension for E.164 string, or None."""
    for key in extension_map:
        if extension_map[key]['caller_id'] == e164:
            return key
    return None

# Return normalized string, if it can be.
# E.164 is +[country code][number]. Three digit numbers are +1[number].
def normalize_number(number):
    # XXX DigitalOcean is not letting us import the phonenumbers library?
    #     We do this klugy partial normalization instead.
    #     We aren't on DigitalOcean anymore and shouln't need this.
    if number.startswith('+'):
        # Temporarily remove a leading +.
        number = number[1:]
    if len(number) == 3:
        # Allow 911, 211, etc. This is how Twilio wants it?
        return '+1' + number
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

def twiml_response(twiml):
    return Response(
        body=str(twiml),
        status_code=200,
        headers={"Content-Type": "text/xml"})

def python_to_twilio_param(v):
    if v == True:
        return 'true'
    elif v == False:
        return 'false'
    raise NotImplementedError

def dial_sip(request, env):
    """Return a TwiML response to dial a SIP extension on the Futel server."""
    metric.publish('dial_sip', request, env)
    to_uri = request.post_fields['To']
    from_uri = request.post_fields['From']

    # XXX are these already sip_to_extension?
    from_extension = sip_to_extension(from_uri)
    to_extension = sip_to_extension(to_uri)
    extensions = get_extensions()
    if to_extension == "#":
        to_extension = extensions[from_extension]['outgoing']
    elif to_extension == "0":
        to_extension = 'operator'

    instance = get_instance(request)
    server_name = f'futel-{instance}.phu73l.net'
    sip_uri = f'sip:{to_extension}@{server_name}'

    # The caller ID is the SIP extension we are calling from, which we assume is E.164.
    extensions = get_extensions()
    caller_id = extensions[from_extension]['caller_id']
    enable_emergency = extensions[from_extension]['enable_emergency']
    enable_emergency = python_to_twilio_param(enable_emergency)

    sip_uri = (f'{sip_uri};'
               f'region=us2?x-callerid={caller_id}&x-enableemergency={enable_emergency}')

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        answer_on_bridge=True,
        action=function_url(request, 'metric_dialer_status'))
    dial.sip(sip_uri)
    # XXX did the Asterisk context go to the parent and hang up, leaving us here?
    return response

def dial_pstn(request, env):
    """Return TwiML to dial PSTN number with attributes from request."""
    metric.publish('dial_pstn', request, env)
    to_uri = request.post_fields['To']
    from_uri = request.post_fields['From']

    to_number = sip_to_extension(to_uri)
    to_number = normalize_number(to_number)
    to_number = transform_number(to_number)
    log(f'to_number: {to_number}')
    if filter_outgoing_number(to_number):
        log(f'filtered to_number: {to_number}')
        return reject(request)

    from_extension = sip_to_extension(from_uri)
    extensions = get_extensions()
    caller_id = extensions[from_extension]['caller_id']

    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    response = VoiceResponse()
    dial = response.dial(
        caller_id=caller_id,
        answer_on_bridge=True,
        action=function_url(request, 'metric_dialer_status'))
    dial.number(to_number)
    metric.publish('dialing', request, env) # We passed the filter.
    return response

def reject(request, env):
    """Return TwiML reject response."""
    metric.publish('reject', request, env)
    response = VoiceResponse()
    response.say(
        "We're sorry, your call cannot be completed as dialed. "
        "Please check the number and try again.");
    response.reject()
    return response
