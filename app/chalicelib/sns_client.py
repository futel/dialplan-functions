"""
Publish messages to sns. We use the same store for all sources,
so any differentation between prod and other hosts must be in the messages.
"""

import json

def _publish(message, arn, env):
    return env['sns_client'].publish(
        TargetArn=arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json')

def publish_log(message, env):
    return _publish(message, env['AWS_LOGS_TOPIC_ARN'], env)

def publish_metric(message, env):
    return _publish(message, env['AWS_METRICS_TOPIC_ARN'], env)
