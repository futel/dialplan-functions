from unittest import mock, TestCase

from chalicelib import metric


request = mock.Mock(
    post_fields={
        'SipDomain': 'direct-futel-prod.sip.twilio.com',
        'From': 'sip:bottles-and-cans-one@direct-futel-prod.sip.twilio.com'},
    context={'domainPrefix':'prod'})
env = {
    'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
    'sns_client': mock.Mock(),
    'stage':'prod'}



class TestMetric(TestCase):

    def test_publish(self):
        self.assertTrue(
            metric.publish('user_event', "user", env))

    def test_publish_twilio_error_foo(self):
        self.assertTrue(
            metric.publish_twilio_error(
                'foo-bar',
                {'resource_sid': 'foo',
                 'service_sid': None,
                 'error_code': '21609',
                 'more_info': {
                     'Msg': 'foo',
                     'invalidStatusCallbackUrl': 'bar',
                     'ErrorCode': '21609',
                     'LogLevel': 'WARNING'},
                 'webhook': {
                     'type': 'application/json',
                     'request': {
                         'url': 'sip:demo-one@direct-futel-stage.sip.twilio.com',
                         'method': None,
                         'headers': {},
                         'parameters': {}},
                     'response': {
                         'status_code': None,
                         'headers': {},
                         'body': None}}},
                env))

    def test_publish_twilio_error_bar(self):
        message = {'resource_sid': 'CA96ec5e33405afd1a43935f0039d1a0af', 'service_sid': None, 'error_code': '11200', 'more_info': {'Msg': 'Got HTTP 502 response to http://10.209.67.130:8080/ivr/outgoing_operator_operator?parent=outgoing_operator_operator&lang=en&iteration=0&stanza=menu', 'ErrorCode': '11200', 'LogLevel': 'ERROR'}, 'webhook': {'type': 'application/json', 'request': {'url': 'http://10.209.67.130:8080/ivr/outgoing_operator_operator?parent=outgoing_operator_operator&lang=en&iteration=0&stanza=menu', 'method': 'POST', 'headers': {}, 'parameters': {'ApiVersion': '2010-04-01', 'CalledZip': '97114', 'Called': '+1503xxxxxxx', 'CallStatus': 'in-progress', 'CalledCity': 'CARLTON', 'From': '+15034448615', 'ToState': 'OR', 'CallerCountry': 'US', 'Direction': 'outbound-api', 'AccountSid': 'ACccee506a7e232c9b6b17175c9e54860c', 'CalledCountry': 'US', 'CallerCity': 'BEAVERTON', 'CallerState': 'OR', 'Caller': '+15034448615', 'FromCountry': 'US', 'ToCity': 'CARLTON', 'ToZip': '97114', 'FromCity': 'BEAVERTON', 'CalledState': 'OR', 'To': '+1503xxxxxxx', 'CallSid': 'CA96ec5e33405afd1a43935f0039d1a0af', 'FromZip': '97229', 'ToCountry': 'US', 'CallerZip': '97229', 'FromState': 'OR'}}, 'response': {'status_code': None, 'headers': {'x-envoy-upstream-service-time': '2', 'x-twilio-reason': 'Blacklisted IP', 'Server': 'envoy', 'Content-Length': '539', 'x-twilio-webhookattempt': '1', 'Date': 'Tue, 24 Sep 2024 23:37:55 GMT', 'Content-Type': 'text/html'}, 'body': 'Twilio was unable to fetch content from: http://10.209.67.130:8080/ivr/outgoing_operator_operator?parent=outgoing_operator_operator&lang=en&iteration=0&stanza=menu\nError: Blacklisted IP 10.209.67.130\nAccount SID: ACccee506a7e232c9b6b17175c9e54860c\nSID: CA96ec5e33405afd1a43935f0039d1a0af\nRequest ID: aa1776c7-a8f2-4adf-9a46-dbb91a97786f\nRemote Host: 10.209.67.130\nRequest Method: POST\nRequest URI: http://10.209.67.130:8080/ivr/outgoing_operator_operator?parent=outgoing_operator_operator&lang=en&iteration=0&stanza=menu\nURL Fragment: true'}}}
        self.assertTrue(
            metric.publish_twilio_error(
                'foo-bar',
                message,
                env))

    def test_event_to_message(self):
        out = {
            "timestamp": "2023-05-11T22:36:13.000489",
            "hostname": "hostname",
            "event": {
                "Event": "UserEvent",
                "endpoint": "endpoint",
                "Channel": "endpoint",
                "UserEvent": "user_event"}}
        got = metric._event_to_message(
            'endpoint', 'user_event', 'hostname')
        del out['timestamp']
        del got['timestamp']
        self.assertEqual(got, out)


if __name__ == '__main__':
    unittest.main()
