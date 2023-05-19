import dial_sip
import util

def main(event, context):
    env = util.get_env()
    return dial_sip.dial_sip(event, context, env)
