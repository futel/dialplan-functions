from assets import extensions
#import json
#import pathlib

def log(msg):
    print(msg)

def twiml_response(twiml):
    return {
        "headers": {"Content-Type": "text/xml"},
        "statusCode": 200,
        "body": str(twiml)}

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
    # name = name + '.json'
    # sdir = source_dir() / 'assets'
    # print(sdir / name)
    # with open(sdir / name) as f:
    #     return json.load(f)

#sip:test@direct-futel-nonemergency-stage.sip.twilio.com
def sip_to_exension(sip_uri):
    """Return the extension from a SIP URI."""
    return sip_uri.split('@')[0].split(':')[1]
