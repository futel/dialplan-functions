from dotenv import load_dotenv
from unittest import mock, TestCase

import metric_dialer_status
import sns_client

class TestSnsClient(TestCase):

    def test_foo(self):
        self.assertEqual(
            sns_client.get_metric_hostname(), 'do-dialplans-stage')

    def test_event_to_message(self):
        event = {
            'channel': 'dummy',
            'user_event': 'dummy'}
        out = {"timestamp": "2023-05-11T22:36:13.000489", "hostname": "hostname", "event": {"Event": "UserEvent", "Channel": "dummy", "UserEvent": "dummy"}}
        got = sns_client.event_to_message(event, 'hostname')
        del out['timestamp']
        del got['timestamp']
        self.assertEqual(got, out)

if __name__ == '__main__':
    unittest.main()
