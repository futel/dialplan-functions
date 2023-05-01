from twilio.twiml.voice_response import VoiceResponse


xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Hello, world!</Say>
</Response>
"""

def top(event):
    response = VoiceResponse()
    response.say('Hello World')
    return {
        "headers": {"Content-Type": "text/xml"},
        "statusCode": 200,
        "body": str(response)}
