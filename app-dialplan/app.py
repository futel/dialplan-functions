"""
Chalice top level module. For a HTTP interactoin, this exists to start the app
to get the request, run a single view function, and return the result. There may
be other actions enabled by chalice, like scheduled tasks.
"""

from chalice import Chalice, Response
import functools
import os
import requests
from twilio.request_validator import RequestValidator
from urllib import parse

from chalicelib import dialers
from chalicelib import env_util
from chalicelib import ops
from chalicelib import util

env = env_util.get_env()
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

def validate_request(request, env):
    validator = RequestValidator(env['TWILIO_AUTH_TOKEN'])
    # XXX We need to reconstruct the URL that we were called with, and we're
    #     doing it wrong! Either we or twilio are not assembling the signature
    #     properly. It appears to happen on requests that are playing a menu
    #     with query params, but it still happens if we test by removing all
    #     query params from the request. It appears to happen when there is a
    #     Digits post param in the request. When that happens, there is also a
    #     'msg':'Gather End' post param sent by twilio, but quoting that
    #     doesn't help.
    host = request.headers['host']
    path = request.context['path']
    url = 'https://' + host + path
    # post_fields = {
    #     requests.utils.quote(v) for (k,v) in request.post_fields.items()}
    post_fields = request.post_fields
    url += '?' + parse.urlencode(request.query_params)
    # Assume it is a POST request.
    return validator.validate(
        url,
        post_fields,
        request.headers.get('X-TWILIO-SIGNATURE', ''))

def setup_request(request):
    """
    Update request for view function.
    Fill post_fields and query_params attributes.
    If post_fields has a From that parses to an extension name, fill from_user.
    Otherwise, fill from_user with the hot-leet placeholder, and optionally
    fill from_number.
    """
    request.post_fields = post_fields(request)
    request.query_params = request.query_params or {}

    from_user = request.post_fields.get('From')
    if not from_user:
        # This is a callback after a twilio call error.
        # For the purposes of metrics the from user is us, the generic system.
        request.from_user = "hot-leet"
        # We shouldn't be accessing this attribute again, it's only here
        # because we are mixing up codebases.
        request.from_number = None
    else:
        from_user = util.sip_to_user(from_user)
        if from_user:
            # This is an outgoing twilio pv call from a sip client, or a
            # status callback after one.
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

# Decorator to set up the view request and response. We need to do this when
# after the app has set up the global request, so this has to be during the call
# to the view, we implement it in a decorator.
def setup(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        # By now the global app has been set up with its request,
        # so we can modify it.
        request = setup_request(app.current_request)
        valid = validate_request(request, env)
        if not valid:
            # XXX We don't actually do anything about an invalid request,
            #     because validation doesn't always succeed.
            util.log("invalid request")
        response = f(request, *args, **kwargs)
        return setup_response(response)
    return decorated


# The route decorator is unexpected. It registers the function object
# being defined with the app. The function reference that we are creating
# here by defining it is never accessed, we throw it away. Probably fun
# to design but needs 4 lines of comments.

@route('/dial_extension/{extension_name}')
@setup
def _index(request, extension_name):
    return dialers.dial_extension(extension_name, request, env)

@route('/dial_e164_extension')
@setup
def _index(request):
    return dialers.dial_e164_extension(request, env)

@route('/dial_outgoing')
@setup
def _index(request):
    return dialers.dial_outgoing(request, env)

@route('/dial_sip_e164')
@setup
def _index(request):
    return dialers.dial_sip_e164(request, env)

@route('/ivr')
@setup
def _index(request):
    return dialers.ivr(None, request, env)

@route('/ivr/{context_name}')
@setup
def _index(request, context_name):
    return dialers.ivr(context_name, request, env)

@route('/enqueue_operator_wait')
@setup
def _index(request):
    return dialers.enqueue_operator_wait(request, env)

@route('/enqueue_operator_record')
@setup
def _index(request):
    return dialers.enqueue_operator_record(request, env)

@route('/outgoing_operator_dialer_status')
@setup
def _index(request):
    return dialers.outgoing_operator_dialer_status(request, env)

@route('/outgoing_operator_leave')
@setup
def _index(request):
    return dialers.outgoing_operator_leave(request, env)

@route('/reject')
@setup
def _index(request):
    return dialers.reject(request, env)

@route('/ops/call_status_exercise')
@setup
def _index(request):
    return ops.call_status_exercise(request, env)

@route('/ops/call_status_outgoing')
@setup
def _index(request):
    return ops.call_status_outgoing(request, env)

@route('/ops/log')
@setup
def _index(request):
    return ops.log(request, env)


# All the startup work we have given lambda is done, log for timing.
# The log before this should be the INIT message.
util.log('app start')
