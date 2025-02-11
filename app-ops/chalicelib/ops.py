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

def _extension():
    """ Return an extension for the exerciser to call. """
    # Extensions of interest.
    # Don't include extensions in workplaces or other environments where we
    # don't want to disturb a human.
    extensions = [
        'alleymaple',
        'alleytwentyseventh',
        # bottles-and-cans-one is only on 12p-9p
        #'bottles-and-cans-one',
        "brazee",
        'cesar-chavez-one',
        'clinton',
        'dome-workshop',
        'fortysecond',
        'ghost-mountain',
        'landline'
    ]

    # Choose the next extension to call modulo the current minute.
    # We want to choose extensions evenly.
    # We hope to not call an extension twice in a row, so we hope we aren't
    # called twice in a minute modulo the number of choices!
    # We hope to not call an extension at the same time every day.
    # minute = datetime.datetime.fromisoformat(event.time).minute
    # choice = minute % len(extensions)
    # extension = extensions[choice]

    # Q&D but incorrect way is to just randomly choose.
    # Deterministic would be much better, same amount of calls per period, etc.
    # Is this random enough when run by lambda? What's the seed?
    extension = random.choice(extensions)
    return extension

# This is intended to shake out errors and other outcomes that indicate the
# connected status of the extensions.
def exercise(event, env):
    """
    SIP call an extension with the twilio API and play a dialplan.
    """
    util.log("exercise")
    stage = util.get_instance(env)
    extension = _extension()
    context = "community_outgoing"
    exercise_one(stage, extension, context, env=env)

def exercise_one(stage, extension, context, env):
    """
    SIP call extension with the twilio API and play a dialplan.
    """
    client = Client(
        env['TWILIO_ACCOUNT_SID'],
        env['TWILIO_AUTH_TOKEN'])
    to = 'sip:{extension}@direct-futel-{stage}.sip.twilio.com'.format(
        extension=extension, stage=stage)
    # Ring timeout in seconds, twilio may add 5s? 20s should give us 4 rings.
    timeout = 20
    # Call time limit in seconds.
    time_limit = 30 * 60
    # URL to return twiml for callee to experience.
    url = "https://{stage}.dialplans.phu73l.net/ivr/{context}".format(
        stage=stage, context=context)
    # URL to be posted with call status.
    status_callback_url = (
        "https://{stage}.dialplans.phu73l.net/ops/call_status_exercise".format(
            stage=stage))

    util.log("calling {}".format(extension))
    return client.calls.create(
        to=to,
        from_="+15034681337",
        url=url,
        timeout=timeout,
        time_limit=time_limit,
        status_callback_event='completed', #['initiated', 'ringing', 'answered']
        status_callback=status_callback_url)
