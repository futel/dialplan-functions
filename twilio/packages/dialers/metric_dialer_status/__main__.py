import metric_dialer_status
import util

def main(event, context):
    env = util.get_env()
    return metric_dialer_status.metric_dialer_status(event, context, env)
