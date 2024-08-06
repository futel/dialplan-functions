"""
Functions for ops HTTP endpoints.
This should probably be an entirely separate project, but the tooling is here.
"""

from . import sns_client
from . import util

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
    message = request.post_fields['Payload']
    util.log(message)
    sns_client.publish_log(message, env)
