import ivr
import util

def main(event, context):
    env = util.get_env()
    return ivr.ivr(event, context, env)
