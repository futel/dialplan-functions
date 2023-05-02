from twilio.twiml.voice_response import VoiceResponse


def top(event):
    response = VoiceResponse()
    response.say('Hello World')
    return {
        "headers": {"Content-Type": "text/xml"},
        "statusCode": 200,
        "body": str(response)}
