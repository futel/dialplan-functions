import dotenv
import json
import sys
from unittest import mock, TestCase

dotenv.load_dotenv('./src/.env')

sys.path.append('./src')
import lambda_function

response = {
    'body': '<?xml version="1.0" encoding="UTF-8"?><Response><Say>We\'re sorry, '
    'your call cannot be completed as dialed. Please check the number and '
    'try again.</Say><Reject /></Response>',
    'headers': {'Content-Type': 'text/xml'},
    'statusCode': 200}


class TestSampleLambda(TestCase):

    def load_sample_event_from_file(self):
        event_file_name = f"test/event.json"
        with open(event_file_name, "r", encoding='UTF-8') as file_handle:
            event = json.load(file_handle)
            return event

    @mock.patch.object(lambda_function, 'metric')
    def test_lambda_handler_valid_event_returns_200(self, _mock_metric):
        test_event = self.load_sample_event_from_file()
        test_return_value = lambda_function.lambda_handler(event=test_event, context=None)
        self.assertEqual(test_return_value, response)
