from unittest import mock, TestCase

from chalicelib import sns_client


class TestSnsClient(TestCase):

    def test_publish_metric_prod(self):
        env = {
            'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
            'sns_client': mock.Mock(),
            'stage': 'prod'}
        sns_client.publish_metric({}, env)
        env['sns_client'].publish.assert_called()

    def test_publish_metric_stage(self):
        env = {
            'AWS_METRICS_TOPIC_ARN': 'AWS_METRICS_TOPIC_ARN',
            'sns_client': mock.Mock(),
            'stage': 'stage'}
        sns_client.publish_metric({}, env)
        env['sns_client'].publish.assert_not_called()

if __name__ == '__main__':
    unittest.main()
