from assets import extensions

import re

def log(msg):
    print(msg)

def twiml_response(twiml):
    return {
        "headers": {"Content-Type": "text/xml"},
        "statusCode": 200,
        "body": str(twiml)}

def python_to_twilio_param(v):
    if v == True:
        return 'true'
    elif v == False:
        return 'false'
    raise NotImplementedError

def get_instance():
    """Return the instance/namespace/environment name eg 'prod', 'stage', 'dev'."""
    # XXX we are stage!
    return 'stage'

def function_url(context, function_name):
    """Return the URL for another function in this package and namespace."""
    package = 'dialplans'
    return context.api_host + '/api/v1/web/' + context.namespace + '/' + package + '/' + function_name

def source_dir():
    """Return the directory that files and directories can be accessed from."""
    return pathlib.Path(__file__).resolve().parent

def get_extensions():
    """Return extensions asset object."""
    return extensions.extensions

#sip:test@direct-futel-nonemergency-stage.sip.twilio.com
def sip_to_extension(sip_uri):
    """Return the extension from a SIP URI, or None."""
    try:
        return sip_uri.split('@')[0].split(':')[1]
    except IndexError:
        return None

def e164_to_extension(e164, extension_map):
    """Return an extension for E.164 string, or None."""
    for key in extension_map:
        if extension_map[key]['caller_id'] == e164:
            return key
    return None

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
