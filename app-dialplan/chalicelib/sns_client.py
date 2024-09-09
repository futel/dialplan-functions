"""
Publish messages to sns. We use the same store for all sources,
so any differentation between prod and other hosts must be in the messages.
"""

import json

def _is_prod(env):
    return env['stage'] == 'prod'

def _publish(message, arn, env):
    return env['sns_client'].publish(
        TargetArn=arn,
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json')

# def publish_log(message, env):
#     return _publish(message, env['AWS_LOGS_TOPIC_ARN'], env)

def publish_metric(message, env):
    if not _is_prod(env):
        # Don't do anything if we aren't on prod. We do this so we don't have to
        # chase down consumers to make sure they aren't using non-prod data,
        # because anything involving looking at data is too complex. It would be
        # better to instead use have separate ARNs for all stages, for debugging.
        return
    return _publish(message, env['AWS_METRICS_TOPIC_ARN'], env)
