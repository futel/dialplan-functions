"""
Download and delete operator messages stored by Twilio Programmable Voice.
"""

import dotenv
import os
from twilio.rest import Client

dotenv.load_dotenv(
    os.path.join(
        os.path.dirname(__file__),
        '..', 'app', 'chalicelib', 'environment', '.env'))

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

# XXX do we need to limit?
recordings = client.recordings.list(limit=20)

for record in recordings:
    print(record.media_url)
    # XXX append .wav or .mp3 to download
    # XXX record.delete()
