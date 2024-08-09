"""
Functions for ops HTTP endpoints.
This should probably be an entirely separate project, but the tooling is here.
"""
import json

from . import metric
from . import sns_client
from . import util

# Prefix for metrics from error log webhook.
event_prefix = "error"

# This is a silly way to validate. The correct way is
# https://www.twilio.com/docs/usage/webhooks/webhooks-security#validating-signatures-from-twilio
def _validate(request, env):
    """Q&D request validation."""
    if env['TWILIO_ACCOUNT_SID'] == request.post_fields['AccountSid']:
        return
    raise NotImplementedError

def log(request, env):
    """HTTP endpoint for doing something with a log message."""
    # The message comes from a twilio error log webhook.
    _validate(request, env)
    # The message is stored in a 'Payload' post param as a json repr.
    message = json.loads(request.post_fields['Payload'])
    util.log(message)
    # Turn the error code in the message into a metric key and publish it.
    event = "{}-{}".format(event_prefix, message.get('error_code'))
    metric.publish_other(event, request, env)
    # Publish the message to our log store.
    # We don't document the message format, so we aren't indicating whether we
    # are prod, stage, or another host.
    sns_client.publish_log(message, env)
