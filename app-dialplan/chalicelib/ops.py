"""
Functions for ops HTTP endpoints.
This should probably be an entirely separate project, but the tooling is here.
"""
import json
from twilio.twiml.voice_response import VoiceResponse

from . import metric
from . import util

# Prefix for metrics from error log webhook.
event_prefix = "twilio-error"

# This is a silly way to validate. The correct way is
# https://www.twilio.com/docs/usage/webhooks/webhooks-security#validating-signatures-from-twilio
def _validate(request, env):
    """Q&D request validation."""
    if env['TWILIO_ACCOUNT_SID'] == request.post_fields['AccountSid']:
        return
    raise NotImplementedError

def _hangup():
    """Return twiml string that hangs up."""
    response = VoiceResponse()
    response.hangup()
    return str(response)

def call_status_exercise(request, env):
    """
    Peform side effects from an outgoing rest api call.
    Return a twiml hangup document string.
    """
    # XXX Need to validate caller.
    # We are metricing the outgoing call even though we don't care so much about
    # that leg, we just want to notice that we are doing something as expected.
    # Any error callback hit by twilio in reaction to that call will tell us
    # about connectivity errors related to the destination extension.
    # This is a twilio REST client outgoing call callback.
    from_user = "hot-leet"

    # Perform the side effects of publishing metrics for call status.
    call_status = request.post_fields.get('CallStatus')
    dial_event = "outgoing_call"
    dial_status_event = "outgoing_dialstatus_" + call_status + '_' + from_user
    metric.publish(dial_event, from_user, env)
    metric.publish(dial_status_event, from_user, env)

    # Perform the side effects of publishing metrics and logs for errors.
    error_code = request.post_fields.get('ErrorCode')
    if error_code:
        error_event = 'error-{}'.format(error_code)
        metric.publish(error_event, from_user, env)
    error_message = request.post_fields.get('ErrorMessage')
    if error_message:
        util.log(error_message)

    return _hangup()

def call_status_pstn(request, env):
    """
    Peform side effects from an outgoing twilio pv pstn dial call.
    Return a twiml hangup document string.
    """
    # XXX Need to validate caller.
    # We don't care who the call was to, that logging happens on another leg.
    # This is a twilio pv dial callback, which we assume uses a sip url for one
    # our clients as the from in the request.
    from_user = util.sip_to_user(request.post_fields['From'])

    # Perform the side effects of publishing metrics for call status.
    call_status = request.post_fields.get('DialCallStatus')
    dial_event = "outgoing_call"
    dial_status_event = (
        "outgoing_dialstatus_" + call_status + '_' + from_user)
    metric.publish(dial_event, from_user, env)
    metric.publish(dial_status_event, from_user, env)

    # Perform the side effects of publishing metrics and logs for errors.
    error_code = request.post_fields.get('ErrorCode')
    if error_code:
        error_event = 'error-{}'.format(error_code)
        metric.publish(error_event, from_user, env)
    error_message = request.post_fields.get('ErrorMessage')
    if error_message:
        util.log(error_message)

    # We should sometimes return twiml to play to notify the caller
    # eg str(util.reject(request, env, reason='busy'))
    return _hangup()

def call_status_sip(request, env):
    """
    Peform side effects from an outgoing twilio pv sip dial call.
    Return a twiml hangup document string.
    """
    # XXX Need to validate caller.
    # We don't care who the call was to, that logging happens on another leg.
    # This is a twilio pv dial callback, which we assume uses a sip url for one
    # our clients as the from in the request.
    from_user = util.sip_to_user(request.post_fields['From'])

    # Perform the side effects of publishing metrics for call status.
    call_status = request.post_fields.get('DialCallStatus')
    dial_event = "outgoing_call"
    dial_status_event = "outgoing_dialstatus_" + call_status + '_' + from_user
    metric.publish(dial_event, from_user, env)
    metric.publish(dial_status_event, from_user, env)

    # Perform the side effects of publishing metrics and logs for errors.
    error_code = request.post_fields.get('ErrorCode')
    if error_code:
        error_event = 'error-{}'.format(error_code)
        metric.publish(error_event, from_user, env)
    error_message = request.post_fields.get('ErrorMessage')
    if error_message:
        util.log(error_message)

    # We should sometimes return twiml to play to notify the caller
    # eg str(util.reject(request, env, reason='busy'))
    return _hangup()

def log(request, env):
    """HTTP endpoint for doing something with a log message."""
    # The request comes from a twilio error log webhook as set up in the
    # twilio-sip-server component.
    _validate(request, env)
    # The message is stored in a 'Payload' post param as a json repr.
    message = json.loads(request.post_fields['Payload'])
    util.log(message)
    # Turn the error code in the message into a metric key and publish it.
    event = "{}-{}".format(event_prefix, message.get('error_code'))
    # The message comes from a twilio error log webhook, so metric that.
    metric.publish_twilio_error(event, message, env)
    # Publish the message to our log store.
    # We don't document the message format, so we aren't indicating whether we
    # are prod, stage, or another host.
    # This is causing s3-event-writer problems, so this is disabled.
    #sns_client.publish_log(message, env)
