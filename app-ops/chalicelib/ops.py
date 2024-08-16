"""
Functions for ops HTTP endpoints.
"""
import datetime
from twilio.rest import Client

from . import util

# This is a silly way to validate. The correct way is
# https://www.twilio.com/docs/usage/webhooks/webhooks-security#validating-signatures-from-twilio
def _validate(request, env):
    """Q&D request validation."""
    if env['TWILIO_ACCOUNT_SID'] == request.post_fields['AccountSid']:
        return
    raise NotImplementedError

def exercise(event, env):
    util.log("exercise")
    # We could use the host header in the request instead?
    stage = env['stage']

    twilio_account_sid = env['TWILIO_ACCOUNT_SID']
    twilio_auth_token = env['TWILIO_AUTH_TOKEN']
    client = Client(twilio_account_sid, twilio_auth_token)

    extensions = [
        #'alleymaple',
        'bottles-and-cans-one',
        'bottles-and-cans-two',
        'cesar-chavez',
        #'clinton',
        'dome-basement',
        'dome-booth',
        'dome-workshop',
        #'fortysecond',
        'ghost-mountain',
        'landline',
        #'souwester'
    ]
    # We want to hit extensions evenly.
    # We have fewer than 24 extensions, so we find the next extension modulo
    # the hour of the day.
    # We assume that we aren't called twice in an hour, and every hour is
    # represented evenly in the long run.
    hour = datetime.datetime.fromisoformat(event.time).hour
    extension = extensions[len(extensions) % hour]

    to = 'sip:{extension}@direct-futel-{stage}.sip.twilio.com'.format(
        extension=extension, stage=stage)
    context = "community_outgoing"
    # URL to return twiml for callee to experience.
    url = "https://{stage}.dialplans.phu73l.net/ivr?context={context}".format(
        stage=stage, context=context)

    util.log(url)

    # XXX Do we need to specify metric_dialer_status as the status_callback?
    #status_callback=statusCallbackUrl,
    #status_callback_event=['initiated', 'ringing', 'answered', 'completed'],
    call = client.calls.create(
        to=to,
        from_="+15034681337",
        url=url)
