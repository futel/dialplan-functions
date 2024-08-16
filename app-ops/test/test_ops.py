from unittest import mock, TestCase

from chalicelib import ops

env = {
    #'AWS_LOGS_TOPIC_ARN': 'AWS_LOGS_TOPIC_ARN',
    #'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
    'TWILIO_ACCOUNT_SID': 'TWILIO_ACCOUNT_SID',
    'TWILIO_AUTH_TOKEN': 'TWILIO_AUTH_TOKEN',
    #'sns_client': mock.Mock()
}

class TestOps(TestCase):
    pass
