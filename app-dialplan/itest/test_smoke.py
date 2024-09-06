import json
import requests
from unittest import mock, TestCase

from chalicelib import env_util

env = env_util.get_env()

def check_response(response, text):
    assert response.status_code == 200, (response, response.text)
    assert response.text == text, (response, response.text)

class TestDialers(TestCase):

    def test_dial_outgoing_e164_pstn(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/dial_outgoing",
            data={
                "To": "sip:5035551212@direct-futel-stage.sip.twilio.com",
                "From": "sip:test-one@direct-futel-stage.sip.twilio.com",
                "SipDomain": "direct-futel-stage.sip.twilio.com"})
        check_response(
            response,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://stage.dialplans.phu73l.net/ops/call_status_pstn" answerOnBridge="true" callerId="+19713512383"><Number>+15035551212</Number></Dial></Response>')

    def test_dial_outgoing_e164_sip(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/dial_outgoing",
            data={
                # cesar-chavez
                "To": "sip:+15039465227@direct-futel-stage.sip.twilio.com",
                "From": "sip:test-one@direct-futel-stage.sip.twilio.com",
                "SipDomain": "direct-futel-stage.sip.twilio.com"})
        check_response(
            response,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://stage.dialplans.phu73l.net/ops/call_status_sip" answerOnBridge="true" callerId="+19713512383"><Sip>sip:cesar-chavez@direct-futel-stage.sip.twilio.com</Sip></Dial></Response>')

    def test_dial_outgoing_pound(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/dial_outgoing",
            data={
                "To": "sip:#@direct-futel-stage.sip.twilio.com",
                "From": "sip:test-one@direct-futel-stage.sip.twilio.com",
                "SipDomain": "direct-futel-stage.sip.twilio.com"})
        check_response(
            response,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Redirect>/ivr</Redirect></Response>')

    def test_dial_outgoing_zero(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/dial_outgoing",
            data={
                "To": "sip:0@direct-futel-stage.sip.twilio.com",
                "From": "sip:test-one@direct-futel-stage.sip.twilio.com",
                "SipDomain": "direct-futel-stage.sip.twilio.com"})
        check_response(
            response,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Gather action="https://stage.dialplans.phu73l.net/ivr/outgoing_operator_caller?parent=outgoing_operator_caller&amp;lang=en&amp;iteration=0&amp;stanza=intro" finishOnKey="" numDigits="1" timeout="0"><Play>https://dialplan-assets.s3.us-west-2.amazonaws.com/en/operator/please-hold.ulaw</Play><Play>https://dialplan-assets.s3.us-west-2.amazonaws.com/en/operator/for-the-next-available-operator.ulaw</Play></Gather><Redirect>https://stage.dialplans.phu73l.net/ivr/outgoing_operator_caller?parent=outgoing_operator_caller&amp;lang=en&amp;iteration=0&amp;stanza=menu</Redirect></Response>')

    def test_dial_sip_e164(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/dial_sip_e164",
            data={
                "To": "+17345476651", # landline
                "From": "+15034681337"})
        check_response(
            response,
            '<?xml version="1.0" encoding="UTF-8"?><Response><Dial action="https://stage.dialplans.phu73l.net/ops/call_status_sip" answerOnBridge="true" callerId="+15034681337"><Sip>sip:landline@direct-futel-stage.sip.twilio.com</Sip></Dial></Response>')


class TestOps(TestCase):

    def test_log(self):
        response = requests.post(
            "https://stage.dialplans.phu73l.net/ops/log",
            data={
                "AccountSid": env['TWILIO_ACCOUNT_SID'],
                "Payload": json.dumps({"resource_sid": "CA47172d59c087d4b182c35ba19d6e058a", "service_sid": None, "error_code": "32009", "more_info": {"Msg": "Your TwiML tried to Dial a Twilio SIP Registered User that is not currently registered", "ErrorCode": "32009,Your TwiML tried to Dial a Twilio SIP Registered User that is not currently registered", "LogLevel": "WARNING"}, "webhook": {"type": "application/json", "request": {"url": "sip:demo-one@direct-futel-stage.sip.twilio.com", "method": "INVITE", "headers": {}, "parameters": {"To": "sip:demo-one@direct-futel-stage.sip.twilio.com"}}, "response": {"status_code": None, "headers": {}, "body": None}}})})
        check_response(response, "null")
