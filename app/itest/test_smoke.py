import requests
from unittest import mock, TestCase

from chalicelib import env_util

env = env_util.get_env()

def check_response(response, text):
    assert response.status_code == 200, (response, response.text)
    assert response.text == text, (response, response.text)

class TestDialers(TestCase):

    def test_dial_outgoing_pstn(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/dial_outgoing",
            data={
                "To": "sip:5035551212@direct-futel-stage.sip.twilio.com",
                "From": "sip:test-one@direct-futel-stage.sip.twilio.com",
                "SipDomain": "direct-futel-stage.sip.twilio.com"})
        check_response(
            response,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://stage.dialplans.phu73l.net/metric_dialer_status" answerOnBridge="true" callerId="+19713512383"><Number>5035551212</Number></Dial></Response>')

    def test_dial_outgoing_pound(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/dial_outgoing",
            data={
                "To": "sip:#@direct-futel-stage.sip.twilio.com",
                "From": "sip:test-one@direct-futel-stage.sip.twilio.com",
                "SipDomain": "direct-futel-stage.sip.twilio.com"})
        check_response(
            response,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Gather action="https://stage.dialplans.phu73l.net/ivr?context=outgoing_safe&amp;parent=outgoing_safe&amp;lang=en&amp;iteration=0&amp;stanza=intro" finishOnKey="" numDigits="1" timeout="0"><Play>https://dialplan-assets.s3.us-west-2.amazonaws.com/en/outgoing/para-espanol.ulaw</Play><Play>https://dialplan-assets.s3.us-west-2.amazonaws.com/en/outgoing/oprima-estrella.ulaw</Play></Gather><Redirect>https://stage.dialplans.phu73l.net/ivr?context=outgoing_safe&amp;parent=outgoing_safe&amp;lang=en&amp;iteration=0&amp;stanza=menu</Redirect></Response>')

    def test_dial_outgoing_zero(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/dial_outgoing",
            data={
                "To": "sip:0@direct-futel-stage.sip.twilio.com",
                "From": "sip:test-one@direct-futel-stage.sip.twilio.com",
                "SipDomain": "direct-futel-stage.sip.twilio.com"})
        check_response(
            response,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Gather action="https://stage.dialplans.phu73l.net/ivr?context=outgoing_operator_caller&amp;parent=outgoing_operator_caller&amp;lang=en&amp;iteration=0&amp;stanza=intro" finishOnKey="" numDigits="1" timeout="0"><Play>https://dialplan-assets.s3.us-west-2.amazonaws.com/en/operator/please-hold.ulaw</Play><Play>https://dialplan-assets.s3.us-west-2.amazonaws.com/en/operator/for-the-next-available-operator.ulaw</Play></Gather><Redirect>https://stage.dialplans.phu73l.net/ivr?context=outgoing_operator_caller&amp;parent=outgoing_operator_caller&amp;lang=en&amp;iteration=0&amp;stanza=menu</Redirect></Response>')


class TestOps(TestCase):

    def test_log(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/ops/log",
            data={
                "AccountSid": env['TWILIO_ACCOUNT_SID'],
                "Payload": "{'foo': 'bar'}"})
        check_response(response, 'null')
