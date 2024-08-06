from unittest import mock, TestCase

from chalicelib import ops
#from chalicelib import ivr_destinations
#from chalicelib import sns_client
#from chalicelib import env_util
from chalicelib import util

env = {'AWS_LOGS_TOPIC_ARN': 'AWS_LOGS_TOPIC_ARN',
       'TWILIO_ACCOUNT_SID': 'TWILIO_ACCOUNT_SID',
       'TWILIO_AUTH_TOKEN': 'TWILIO_AUTH_TOKEN',
       'sns_client': mock.Mock()}

class TestOps(TestCase):

    def test_log(self):#, _mock_metric):
        request = mock.Mock(
            post_fields={
                'AccountSid': 'TWILIO_ACCOUNT_SID',
                'Payload': '7B%22resource_sid%22%3A%22CA8339b5eb12c2b5bcd3e5e21dd836855a%22%2C%22service_sid%22%3Anull%2C%22error_code%22%3A%2232009%22%2C%22more_info%22%3A%7B%22Msg%22%3A%22Your%20TwiML%20tried%20to%20Dial%20a%20Twilio%20SIP%20Registered%20User%20that%20is%20not%20currently%20registered%22%2C%22ErrorCode%22%3A%2232009%2CYour%20TwiML%20tried%20to%20Dial%20a%20Twilio%20SIP%20Registered%20User%20that%20is%20not%20currently%20registered%22%2C%22LogLevel%22%3A%22WARNING%22%7D%2C%22webhook%22%3A%7B%22type%22%3A%22application%2Fjson%22%2C%22request%22%3A%7B%22url%22%3A%22sip%3Alandline%40direct-futel-prod.sip.twilio.com%22%2C%22method%22%3A%22INVITE%22%2C%22headers%22%3A%7B%7D%2C%22parameters%22%3A%7B%22To%22%3A%22sip%3Alandline%40direct-futel-prod.sip.twilio.com%22%7D%7D%2C%22response%22%3A%7B%22status_code%22%3Anull%2C%22headers%22%3A%7B%7D%2C%22body%22%3Anull%7D%7D%7D'}
        )
        got = ops.log(request, env)
        self.assertEqual(got, None)
