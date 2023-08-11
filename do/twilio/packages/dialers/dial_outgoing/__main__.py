import dial_outgoing
import util

def main(event, context):
    env = util.get_env()
    return dial_outgoing.dial_outgoing(event, context, env)
