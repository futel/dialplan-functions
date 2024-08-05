import json

def publish(message, env):
    return env['sns_client'].publish(
        TargetArn=env['AWS_METRICS_TOPIC_ARN'],
        Message=json.dumps({'default': json.dumps(message)}),
        MessageStructure='json')
