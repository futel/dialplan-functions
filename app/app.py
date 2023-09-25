import boto3
from chalice import Chalice, Response
import dotenv
from urllib import parse

from chalicelib import dialers
from chalicelib import env_util
from chalicelib import util

dotenv.load_dotenv(os.path.join(
    os.path.dirname(__file__), 'environment', '.env'))

env = env_util.get_env()
env['extensions'] = env_util.get_extensions()
env['ivrs'] = env_util.get_ivrs()
env['sns_client'] = boto3.client('sns')

app = Chalice(app_name='app')


def post_fields(request):
    """Return the fields from a POST request."""
    return dict(
        parse.parse_qsl(request.raw_body.decode('UTF-8')))

def setup(func):
    env = util.get_env()
    request = app.current_request
    request.post_fields = post_fields(request)
    response = func(request, env)
    return util.twiml_response(response)

def route(path):
    """Decorator which curries app.route"""
    # Yes, call app.route() to return the decorator function.
    return app.route(path, methods=['POST'], content_types=['application/x-www-form-urlencoded'])

# The route decorator is unexpected. It registers the function object
# being defined with the app. We function reference that we are creating
# here by defining it is never accessed, we throw it away. Probably fun
# to design but needs 4 lines of comments.
# XXX make these private to be more explicit.
@route('/dial_outgoing')
def index():
    return setup(dialers.dial_outgoing)

@route('/dial_sip_e164')
def index():
    return setup(dialers.dial_sip_e164)

@route('/ivr')
def index():
    return setup(dialers.ivr)

@route('/metric_dialer_status')
def index():
    return setup(dialers.metric_dialer_status)


# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
