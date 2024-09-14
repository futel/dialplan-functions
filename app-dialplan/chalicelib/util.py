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

def log(msg):
    print(msg)

def log_request(request):
    msg = 'request '
    msg += 'query_params:{} '.format(request.query_params)
    msg += 'uri_params:{} '.format(request.uri_params)
    msg += 'path:{} '.format(request.path)
    msg += 'raw_body:{}'.format(request.raw_body)
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

def function_url(request, function_name, params=None):
    """
    Return the URL for another function served by the same host.
    """
    # All functions HTTPS, top-level on the same host.
    # Do we need this, isn't this the default?
    url = 'https://' + request.headers['host'] + '/' + function_name
    if params:
       # XXX We are putting URL arguments on a POST that may have
       #     body parameters. Get around this by using path?
       params = parse.urlencode(params)
       url += '?' + params
    return url

#sip:test@direct-futel-nonemergency-stage.sip.twilio.com
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
    """Return an extension key for E.164 string, or None."""
    # These are attributes of the implicit incoming extension.
    if e164 == "+15034681337":
        return "hot-leet"
    for key in extension_map:
        if extension_map[key]['caller_id'] == e164:
            return key
    # Are we in an unknown state if we get here?
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

def filter_outgoing_number(number, enable_emergency):
    """Return True if number should be filtered."""
    if number == '+911':
        return not enable_emergency
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
    # XXX Should specify timeout in seconds, default is 4h.
    dial = response.dial(answer_on_bridge=True)
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

def dial_pstn(to_number, from_extension, request, env):
    """Return TwiML to dial PSTN number with attributes from request."""
    caller_id = from_extension['caller_id']

    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    response = VoiceResponse()
    dial = response.dial(
        caller_id=caller_id,
        answer_on_bridge=True,
        action=function_url(request, 'ops/call_status_pstn'))
    dial.number(to_number)
    return response
