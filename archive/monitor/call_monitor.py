"""Call a SIP number with a monitoring status callback."""

import dotenv
dotenv.load_dotenv()

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']

client = Client(account_sid, auth_token)

# Python version of the following:
# // eg 'https://monitor-666-dev.twil.io/status';
# const statusCallbackUrl = 'dummy';
statusCallbackUrl = 'dummy'
sipDomain = "direct-futel-dev.sip.twilio.com"

toNumber = '+15034681337'
fromNumber = '+15034681337'
to = "sip:${toNumber}@${sipDomain}".format(
    toNumber=toNumber, sipDomain=sipDomain)

call = client.calls.create(
    status_callback=statusCallbackUrl,
    status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
    status_callback_method='POST',
    url='http://demo.twilio.com/docs/voice.xml',
    to=to,
    from_=fromNumber)

print(call.sid)
