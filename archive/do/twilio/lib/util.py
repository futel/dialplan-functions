from assets import extensions

import os
import re
import sys
from twilio.twiml.voice_response import VoiceResponse
from urllib import parse

def log(msg):
    print(msg, file=sys.stderr)

def get_env():
    return {
        'ASSET_HOST': os.environ['ASSET_HOST'],
        'AWS_ACCESS_KEY_ID': os.environ['AWS_ACCESS_KEY_ID'],
        'AWS_SECRET_ACCESS_KEY': os.environ['AWS_SECRET_ACCESS_KEY'],
        'AWS_TOPIC_ARN': os.environ['AWS_TOPIC_ARN'],
        'INSTANCE': os.environ['INSTANCE']}

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

def get_instance(env):
    """Return the instance/namespace/environment name eg 'prod', 'stage', 'dev'."""
    return env['INSTANCE']

def function_url(context, function_name, params=None):
    """
    Return the URL for another function in this package and namespace.
    """
    package = 'dialers'
    url = context.api_host + '/api/v1/web/' + context.namespace + '/' + package + '/' + function_name
    if params:
        params = parse.urlencode(params)
        url += '?' + params
    return url

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

def dial_sip_futel(to_extension, from_extension, context, env):
    """Return a TwiML response to dial a SIP extension on the Futel server."""
    instance = get_instance(env)

    # The caller ID is the SIP extension we are calling from, which we assume is E.164.
    extensions = get_extensions()
    caller_id = extensions[from_extension]['caller_id']
    enable_emergency = extensions[from_extension]['enable_emergency']
    enable_emergency = python_to_twilio_param(enable_emergency)

    sip_uri = (f'sip:{to_extension}@futel-{instance}.phu73l.net;'
               f'region=us2?x-callerid={caller_id}&x-enableemergency={enable_emergency}')

    response = VoiceResponse()
    # XXX default timeLimit is 4 hours, should be smaller, in seconds
    dial = response.dial(
        answer_on_bridge=True,
        action=function_url(context, 'metric_dialer_status'))
    dial.sip(sip_uri)
    # XXX did the Asterisk context go to the parent and hang up, leaving us here?
    return response
    return util.twiml_response(response)
