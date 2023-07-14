import dial_pstn
import util

def main(event, context):
    env = util.get_env()
    return dial_pstn.dial_pstn(event, context, env)
