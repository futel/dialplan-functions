# TwiML dialer suitable as the destination for a TwiML <redirect> verb.

from twilio.twiml.voice_response import VoiceResponse


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

def dialer(event, context):
    """Return TwiML to dial number with attributes from event."""
    number = event['number']
    caller_id = event['caller_id']
    response = VoiceResponse()
    dial = response.dial(
        caller_id=caller_id,
        answer_on_bridge=True,
        action=function_url(context, 'dialer_status'))
    dial.number(number)
    response.append(dial)
    return twiml_response(response)
