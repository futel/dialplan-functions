"""
Functions for ops HTTP endpoints.
This should probably be an entirely separate project, but the tooling is here.
"""
import json
from twilio.twiml.voice_response import VoiceResponse

from . import ivrs
from . import metric
from . import util

# Prefix for metrics from error log webhook.
event_prefix = "twilio-error"

# This is a silly way to validate. The correct way is
# https://www.twilio.com/docs/usage/webhooks/webhooks-security#validating-signatures-from-twilio
def _validate(request, env):
    """Q&D request validation."""
    # XXX Disabled to faciliate testing, implement real validation before
    #     there are attribute to protect or someone decides to make metrics!
    return None
    #if env['TWILIO_ACCOUNT_SID'] == request.post_fields['AccountSid']:
    #    return
    #raise NotImplementedError

def _hangup():
    """Return twiml string that hangs up."""
    response = VoiceResponse()
    response.hangup()
    return str(response)

def _metric_status(call_status, from_user, env):
    """
    Perform the side effects of publishing metrics and logs for call status.
    """
    dial_event = "outgoing_call"
    dial_status_event = "outgoing_dialstatus_" + call_status
    metric.publish(dial_event, from_user, env)
    metric.publish(dial_status_event, from_user, env)

def _metric_log_error(request, from_user, env):
    """
    Perform the side effects of publishing metrics and logs for errors, if
    they are indicated by the request.
    """
    error_code = request.post_fields.get('ErrorCode')
    if error_code:
        error_event = 'error-{}'.format(error_code)
        metric.publish(error_event, from_user, env)
    error_message = request.post_fields.get('ErrorMessage')
    if error_message:
        util.log(error_message)

def call_status_exercise(request, env):
    """
    Peform side effects from an outgoing rest api call.
    Return a twiml hangup document string.
    """
    # XXX Need to validate caller.e
    # XXX This is just call_status_outgoing with a different request field?
    from_user = request.from_user
    call_status = request.post_fields.get('CallStatus')

    _metric_status(call_status, from_user, env)
    _metric_log_error(request, from_user, env)

    return _hangup()

def call_status_outgoing(request, env):
    """
    Peform side effects from an outgoing twilio pv call.
    Return a twiml hangup document string.
    """
    # XXX Need to validate caller.
    from_user = request.from_user
    call_status = request.post_fields.get('DialCallStatus')

    _metric_status(call_status, from_user, env)
    _metric_log_error(request, from_user, env)

    if call_status == 'busy':
        # Play a sound effect. The caller should be getting a proper status and
        # we'd rather not be involved by now but we're just writing twiml
        # documents here.
        response = VoiceResponse()
        # XXX This sound file is not in the ivrs structure, so it isn't checked.
        response.play(
            ivrs.sound_url(
                'busy-signal',
                'sound',
                'ops',
                env))
        response.hangup()
        return str(response)

    return _hangup()

def log(request, env):
    """HTTP endpoint for doing something with a log message."""
    # The request comes from a twilio error log webhook as set up in the
    # twilio-sip-server component.
    _validate(request, env)
    # The message is stored in a 'Payload' post param as a json repr.
    message = json.loads(request.post_fields['Payload'])
    util.log(message)

    # Are we coming from a twilio error log webhook?
    try:
        webhook_request = message['webhook']['request']
    except:
        # Whatever, twilio gives us only one webhook, and errors and warnings
        # from all kinds of projects go here.
        return

    # Turn the error code in the message into a metric key and publish it.
    event = "{}-{}".format(event_prefix, message.get('error_code'))
    # The message comes from a twilio error log webhook, so metric that.
    metric.publish_twilio_error(event, webhook_request, env)
    # Publish the message to our log store.
    # We don't document the message format, so we aren't indicating whether we
    # are prod, stage, or another host.
    # This is causing s3-event-writer problems, so this is disabled.
    #sns_client.publish_log(message, env)
