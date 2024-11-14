from twilio.twiml.voice_response import VoiceResponse
from urllib import parse

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

dial_max = 60 * 60              # 60 minutes in seconds

def log(msg):
    print(msg)

def log_request(request):
    msg = 'request '
    msg += 'query_params:{} '.format(request.query_params)
    msg += 'uri_params:{} '.format(request.uri_params)
    msg += 'post_fields:{} '.format(request.post_fields)
    msg += 'path:{} '.format(request.path)
    log(msg)

def log_response(response):
    msg = 'response '
    msg += 'status_code:{} '.format(response.status_code)
    msg += 'body:{}'.format(response.body)
    log(msg)

def get_instance(env):
    """
    Return the deployment environment name eg 'prod', 'stage', 'dev'.
    """
    return env['stage']

def function_url(function_name, params=None):
    """
    Return the URL for another function served by the same host.
    """
    url = function_name
    if params:
        # Don't serialize Nones.
        params = {k:v for (k,v) in params.items() if v is not None}
        params = parse.urlencode(params)
        url += '?' + params
    return url

#sip:test@direct-futel-stage.sip.twilio.com
def sip_to_user(sip_uri):
    """Return the user from a SIP URI, or None."""
    try:
        user = sip_uri.split('@')[0].split(':')[1]
        user = parse.unquote(user)
        return user
    except IndexError:
        return None

def sip_to_extension(sip_user, env):
    """Return the extension from a SIP user, or None."""
    return env['extensions'].get(sip_user)

def e164_to_extension(e164, extension_map):
    """
    Return the key for the extension matching the given E.164 string, or None.
    """
    if e164 == "+15034681337":
        # The incoming number that we don't want to match. Extensions use this
        # for their caller id when they don't have one.
        return None
    for key in extension_map:
        if extension_map[key]['caller_id'] == e164:
            return key
    # Are we in an unknown state if we get here? We didn't expect to look up a
    # callerid without finding one?
    return None

def normalize_number(number):
    """
    Return a guess of a normalized phone number string.
    Strings are normalized to E.164 +[country code][number]
    or +1[number] for three digit numbers.
    """
    # XXX DigitalOcean is not letting us import the phonenumbers library?
    #     We do this klugy partial normalization instead.
    #     We aren't on DigitalOcean anymore and shouldn't need this.
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

def filter_outgoing_number(number, enable_emergency):
    """
    Return True if number should be filtered.
    Number can be E.164 or a 3 digit service number
    formatted with the "+1" prefix.
    """
    if number in ('+1911', '+1933'):
        return not enable_emergency
    if len(number) == 5:
        # Accept +1911, +1211, etc.
        return False
    if not (number.startswith('+' + usa_code) or
            number.startswith('+' + mexico_code)):
        # Not NANPA or Mexico.
        return True
    # Should we validate US length here?
    # Can we validate Mexico length here?
    # Reject expensive NANPA numbers.
    # Note that Twilio might still reject some NANPA,
    # depending on settings.
    for prefix in premium_nanpa_codes:
        if number.startswith('+1' + prefix):
            return True
    return False

def python_to_twilio_param(v):
    if v == True:
        return 'true'
    elif v == False:
        return 'false'
    raise NotImplementedError

def dial_sip_asterisk(extension, from_user, env):
    """Return a TwiML response to dial a SIP extension on the asterisk."""
    from_extension = env['extensions'][from_user]

    if extension == "#":
        extension = from_extension['outgoing']
    elif extension == "0":
        extension = 'operator'

    instance = get_instance(env)
    server_name = f'futel-{instance}.phu73l.net'
    sip_uri = f'sip:{extension}@{server_name}'

    caller_id = from_extension['caller_id']
    enable_emergency = from_extension['enable_emergency']
    enable_emergency = python_to_twilio_param(enable_emergency)

    sip_uri = (f'{sip_uri};'
               f'region=us2?x-callerid={caller_id}&x-enableemergency={enable_emergency}')

    # Create and return a response document.
    response = VoiceResponse()
    dial = response.dial(
        answer_on_bridge=True,
        time_limit=dial_max)
    dial.sip(sip_uri)
    # Don't specify anything after the dial. Assume the call will be hung up.
    # Don't bother with an action callback to be called with the outcome,
    # don't try to side effect like log or metric the outcome.
    return response

def deserialize_pstn(request):
    """Return to attribute from request for a dial_pstn call."""
    # If there is a Digits in post_fields, use that.
    # Otherwise, extract from SIP URI in To from post_fields.
    to_number = request.post_fields.get('Digits')
    if not to_number:
        to_uri = request.post_fields['To']
        to_number = sip_to_user(to_uri)
    return to_number

def pstn_number(number, enable_emergency):
    """Return normalized and transformed number, or None."""
    number = normalize_number(number)
    number = transform_number(number)
    if filter_outgoing_number(number, enable_emergency):
        return None
    return number

def dial_pstn(to_number, from_extension, request):
    """Return TwiML to dial PSTN number with attributes from request."""
    caller_id = from_extension['caller_id']

    response = VoiceResponse()
    dial = response.dial(
        caller_id=caller_id,
        answer_on_bridge=True,
        time_limit=dial_max,
        action='/ops/call_status_outgoing')
    dial.number(to_number)
    return response
