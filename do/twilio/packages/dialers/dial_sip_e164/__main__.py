import dial_sip_e164
import util

def main(event, context):
    env = util.get_env()
    return dial_sip_e164.dial_sip_e164(event, context, env)
