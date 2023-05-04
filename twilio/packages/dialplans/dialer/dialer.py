from twilio.twiml.voice_response import VoiceResponse


def log(msg):
    print(msg)

def twiml_response(twiml):
    return {
        "headers": {"Content-Type": "text/xml"},
        "statusCode": 200,
        "body": str(twiml)}

def dialer(event, context):
    """Return TwiML to dial number with attributes from event."""
    number = event['number']
    caller_id = event['caller_id']
    response = VoiceResponse()
    # XXX action
    dial = response.dial(
        caller_id=caller_id, answer_on_bridge=True)
    dial.number(number)
    response.append(dial)
    return twiml_response(response)
