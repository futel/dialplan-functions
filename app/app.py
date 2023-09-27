import boto3
from chalice import Chalice, Response
import functools
import os
from urllib import parse

from chalicelib import dialers
from chalicelib import env_util
from chalicelib import util

env = env_util.get_env()
env['extensions'] = env_util.get_extensions()
env['ivrs'] = env_util.get_ivrs()
env['sns_client'] = boto3.client('sns')

app = Chalice(app_name='app')


def post_fields(request):
    """Return the fields from a POST request."""
    return dict(
        parse.parse_qsl(request.raw_body.decode('UTF-8')))

def route(path):
    """Decorator which curries app.route"""
    # Yes, call app.route() to return the decorator function.
    return app.route(
        path,
        methods=['POST'],
        content_types=['application/x-www-form-urlencoded'])

def setup(func):
    """Decorator to log, pass arguments to the view function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        util.log_request(app.current_request)
        response = func(app.current_request, env)
        util.log_response(response)
        return response
    return wrapper

@app.middleware('http')
def request_response_middleware(event, get_response):
    event.post_fields = post_fields(event)
    event.query_params = event.query_params or {}
    # We have to bundle everyhing in the event,
    # we can't change the function signature.
    # XXX not anymore?
    event.env = env
    response = get_response(event)
    response.headers["Content-Type"] = "text/xml"
    return response

# The route decorator is unexpected. It registers the function object
# being defined with the app. We function reference that we are creating
# here by defining it is never accessed, we throw it away. Probably fun
# to design but needs 4 lines of comments.
@route('/dial_outgoing')
@setup
def _index(request, env):
    return dialers.dial_outgoing(request, env)

@route('/dial_sip_e164')
@setup
def _index(request, env):
    return dialers.dial_sip_e164(request, env)

@route('/ivr')
@setup
def _index(request, env):
    return dialers.ivr(request, env)

@route('/metric_dialer_status')
@setup
def _index(request, env):
    return dialers.metric_dialer_status(request, env)
