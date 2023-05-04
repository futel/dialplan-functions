import unittest
import dialer


out = {'headers': {'Content-Type': 'text/xml'}, 'statusCode': 200, 'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Dial answerOnBridge="true" callerId="caller_id"><Number>number</Number></Dial><Dial answerOnBridge="true" callerId="caller_id"><Number>number</Number></Dial></Response>'}

class TestDialer(unittest.TestCase):

    def test_foo(self):
        event = {'number': 'number', 'caller_id': 'caller_id'}
        got = dialer.dialer(event, None)
        self.assertEqual(out, got)


if __name__ == '__main__':
    unittest.main()
