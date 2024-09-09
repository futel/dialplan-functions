"""
Functions for ops HTTP endpoints.
"""
import datetime
import random
from twilio.rest import Client

from . import util

# This is a silly way to validate. The correct way is
# https://www.twilio.com/docs/usage/webhooks/webhooks-security#validating-signatures-from-twilio
def _validate(request, env):
    """Q&D request validation."""
    if env['TWILIO_ACCOUNT_SID'] == request.post_fields['AccountSid']:
        return
    raise NotImplementedError

# This is intended to shake out errors and other outcomes that indicate the
# connected status of the extensions.
def exercise(event, env):
    """
    Call the SIP URI of an extension and play a dialplan with the twilio API.
    """
    util.log("exercise")
    stage = util.get_instance(env)

    twilio_account_sid = env['TWILIO_ACCOUNT_SID']
    twilio_auth_token = env['TWILIO_AUTH_TOKEN']
    client = Client(twilio_account_sid, twilio_auth_token)

    # Extensions of interest.
    # Don't include extensions in workplaces or other environments where we
    # don't want to disturb a human.
    extensions = [
        #'alleymaple',
        'bottles-and-cans-one',
        #'bottles-and-cans-two',
        #'breckenridge',
        'cesar-chavez',
        #'clinton',
        'dome-basement',
        'dome-booth',
        'dome-workshop',
        'fortysecond',
        'ghost-mountain',
        'landline',
        #'souwester'
    ]
    # Choose the next extension to call modulo the current minute.
    # We want to choose extensions evenly.
    # We hope not to call an extension twice in a row, so we hope we aren't
    # called twice in a minute or minute modulo the number of choices!
    # minute = datetime.datetime.fromisoformat(event.time).minute
    # choice = minute % len(extensions)
    # extension = extensions[choice]
    # Bogus, we would rather be deterministic, hope the seed is correct, etc.
    extension = random.choice(extensions)

    to = 'sip:{extension}@direct-futel-{stage}.sip.twilio.com'.format(
        extension=extension, stage=stage)
    context = "community_outgoing"
    # URL to return twiml for callee to experience.
    url = "https://{stage}.dialplans.phu73l.net/ivr?context={context}".format(
        stage=stage, context=context)
    # URL to be posted with call status.
    status_callback_url = (
        "https://{stage}.dialplans.phu73l.net/ops/call_status_exercise".format(
            stage=stage))

    util.log("calling {}".format(extension))
    call = client.calls.create(
        to=to,
        from_="+15034681337",
        url=url,
        status_callback_event='completed', #['initiated', 'ringing', 'answered']
        status_callback=status_callback_url)
