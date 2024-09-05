import boto3
from chalice import Chalice, Response
import functools
import os
from urllib import parse

from chalicelib import dialers
from chalicelib import env_util
from chalicelib import ops
from chalicelib import util

env = env_util.get_env()
# We don't always need all of this, we could be lazy?
env['extensions'] = env_util.get_extensions()
env['ivrs'] = env_util.get_ivrs()
env['sns_client'] = boto3.client('sns')

app = Chalice(app_name='dialplan')

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
    """Decorator to set up request and response of the view function."""
    @functools.wraps(func)
    def wrapper():
        request = setup_request(app.current_request)
        util.log_request(request)
        response = func(request, env)
        response = setup_response(response)
        util.log_response(response)
        return response
    return wrapper

def setup_request(request):
    request.post_fields = post_fields(request)
    request.query_params = request.query_params or {}
    # We can use Direction to tell how to parse out from_user?
    from_user = request.post_fields.get('From')
    if from_user:
        from_user = util.sip_to_user(from_user)
    if from_user:
        # This is an outgoing twilio pv call from a sip client, or a callback
        # after one.
        request.from_user = from_user
    else:
        # This is an incoming call from a twilio phone number to an e164 number
        # for an extension, or it is an outgoing call from a twilio REST client.
        # For the purposes of metrics it is from us, the generic system.
        request.from_user = "hot-leet"
    return request

def setup_response(response):
    response = Response(response)
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

@route('/enqueue_operator_wait')
@setup
def _index(request, env):
    return dialers.enqueue_operator_wait(request, env)

@route('/enqueue_operator_record')
@setup
def _index(request, env):
    return dialers.enqueue_operator_record(request, env)

@route('/outgoing_operator_dialer_status')
@setup
def _index(request, env):
    return dialers.outgoing_operator_dialer_status(request, env)

@route('/outgoing_operator_leave')
@setup
def _index(request, env):
    return dialers.outgoing_operator_leave(request, env)

@route('/reject')
@setup
def _index(request, env):
    return dialers.reject(request, env)

@route('/ops/call_status_exercise')
@setup
def _index(request, env):
    return ops.call_status_exercise(request, env)

@route('/ops/call_status_pstn')
@setup
def _index(request, env):
    return ops.call_status_pstn(request, env)

@route('/ops/call_status_sip')
@setup
def _index(request, env):
    return ops.call_status_sip(request, env)

@route('/ops/log')
@setup
def _index(request, env):
    return ops.log(request, env)


# All the startup work we have given lambda is done, log for timing.
# The log before this should be the INIT message.
util.log('app start')
