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

def setup_request(request):
    """
    Update request.
    Fill post_fields and query_params attributes.
    If post_fields has a From that parses to an extension name, fill from_user.
    Otherwise, fill from_user with the hot-leet placeholder, and optionally
    fill from_number.
    """
    request.post_fields = post_fields(request)
    request.query_params = request.query_params or {}

    from_user = request.post_fields.get('From')
    if not from_user:
        # This is a callback call from a twilio call error.
        # For the purposes of metrics the from user is us, the generic system.
        request.from_user = "hot-leet"
        # We shouldn't be accessing this attribute again, it's only here
        # because we are mixing up codebases.
        request.from_number = None
    else:
        from_user = util.sip_to_user(from_user)
        if from_user:
            # This is an outgoing twilio pv call from a sip client, or a
            # callback after one.
            request.from_user = from_user
            # There may or may not be a phone number associated with this user.
            # Since this is an outgoing call, if we want to associate a
            # caller id later, we will have to look it up then.
            request.from_number = None
        else:
            # This is an incoming call from a twilio phone number to an e164
            # number for an extension, or it is an outgoing call from a
            # twilio REST client.
            # The Direction post_field could be used to determine which it is.
            # For the purposes of metrics the from user is us.
            request.from_user = "hot-leet"
            # The From field is the number the caller gave us. We don't want it
            # in a metric or other non-ephemeral storage down the line.
            request.from_number = request.post_fields.get('From')

    util.log_request(request)
    return request

def setup_response(response):
    response = Response(response)
    response.headers["Content-Type"] = "text/xml"
    util.log_response(response)
    return response

# The route decorator is unexpected. It registers the function object
# being defined with the app. The function reference that we are creating
# here by defining it is never accessed, we throw it away. Probably fun
# to design but needs 4 lines of comments.

@route('/dial_extension/{extension_name}')
def _index(extension_name):
    request = setup_request(app.current_request)
    response = dialers.dial_extension(extension_name, request, env)
    return setup_response(response)

@route('/dial_e164_extension')
def _index():
    request = setup_request(app.current_request)
    response = dialers.dial_e164_extension(request, env)
    return setup_response(response)

@route('/dial_outgoing')
def _index():
    request = setup_request(app.current_request)
    response = dialers.dial_outgoing(request, env)
    return setup_response(response)

@route('/dial_sip_e164')
def _index():
    request = setup_request(app.current_request)
    response = dialers.dial_sip_e164(request, env)
    return setup_response(response)

@route('/ivr')
def _index():
    request = setup_request(app.current_request)
    response = dialers.ivr(None, request, env)
    return setup_response(response)

@route('/ivr/{context_name}')
def _index(context_name):
    request = setup_request(app.current_request)
    response = dialers.ivr(context_name, request, env)
    return setup_response(response)

@route('/enqueue_operator_wait')
def _index():
    request = setup_request(app.current_request)
    response = dialers.enqueue_operator_wait(request, env)
    return setup_response(response)

@route('/enqueue_operator_record')
def _index():
    request = setup_request(app.current_request)
    response = dialers.enqueue_operator_record(request, env)
    return setup_response(response)

@route('/outgoing_operator_dialer_status')
def _index():
    request = setup_request(app.current_request)
    response = dialers.outgoing_operator_dialer_status(request, env)
    return setup_response(response)

@route('/outgoing_operator_leave')
def _index():
    request = setup_request(app.current_request)
    response = dialers.outgoing_operator_leave(request, env)
    return setup_response(response)

@route('/reject')
def _index():
    request = setup_request(app.current_request)
    response = dialers.reject(request, env)
    return setup_response(response)

@route('/ops/call_status_exercise')
def _index():
    request = setup_request(app.current_request)
    response = ops.call_status_exercise(request, env)
    return setup_response(response)

@route('/ops/call_status_pstn')
def _index():
    request = setup_request(app.current_request)
    response = ops.call_status_pstn(request, env)
    return setup_response(response)

@route('/ops/call_status_sip')
def _index():
    request = setup_request(app.current_request)
    response = ops.call_status_sip(request, env)
    return setup_response(response)

@route('/ops/log')
def _index():
    request = setup_request(app.current_request)
    response = ops.log(request, env)
    return setup_response(response)


# All the startup work we have given lambda is done, log for timing.
# The log before this should be the INIT message.
util.log('app start')
