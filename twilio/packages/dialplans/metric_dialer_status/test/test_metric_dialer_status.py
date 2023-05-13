from unittest import mock, TestCase
import metric_dialer_status

class TestMericDialerStatus(TestCase):

    def test_event_to_events_outgoing(self):
        event = {'From':
                 'sip:test@direct-futel-nonemergency-stage.sip.twilio.com',
                 'To': 'to',
                 'DialCallStatus': 'completed'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        got = metric_dialer_status.event_to_events(event)
        self.assertEqual(got,
                         ({'channel': 'test', 'user_event': 'outgoing_call'}, {'endpoint': 'test', 'channel': 'test', 'user_event': 'outgoing_dialstatus_completed_test'}))

    def test_e164(self):
        event = {'From': '+19713512383',
                 'To': '+19713512383',
                 'DialCallStatus': 'completed'}
        context = mock.Mock(api_host='api_host', namespace='namespace')
        got = metric_dialer_status.event_to_events(event)
        self.assertEqual(got, ({'channel': 'test', 'user_event': 'incoming_call'}, {'endpoint': 'test', 'channel': 'test', 'user_event': 'incoming_dialstatus_completed_test'}))

if __name__ == '__main__':
    unittest.main()
