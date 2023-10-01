import reject
import util

def main(event, context):
    env = util.get_env()
    return reject.reject(event, context)
