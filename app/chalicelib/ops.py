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
    """HTTP endpoint for sending a log message."""
    _validate(request, env)
    message = json.loads(request.post_fields['Payload'])
    util.log(message)
    event = "{}-{}".format(event_prefix, message['error_code'])
    metric.publish_other(event, request, env)
    sns_client.publish_log(message, env)
