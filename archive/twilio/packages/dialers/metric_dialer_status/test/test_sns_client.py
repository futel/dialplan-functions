from dotenv import load_dotenv
from unittest import mock, TestCase

import metric_dialer_status
import sns_client

class TestSnsClient(TestCase):

    def test_foo(self):
        env = {'INSTANCE': 'stage'}
        self.assertEqual(
            sns_client.get_metric_hostname(env), 'do-functions-stage')

    def test_event_to_message(self):
        out = {"timestamp": "2023-05-11T22:36:13.000489", "hostname": "hostname", "event": {"Event": "UserEvent", "endpoint": "endpoint", "Channel": "endpoint", "UserEvent": "user_event"}}
        got = sns_client.event_to_message(
            'endpoint', 'user_event', 'hostname')
        del out['timestamp']
        del got['timestamp']
        self.assertEqual(got, out)

if __name__ == '__main__':
    unittest.main()
