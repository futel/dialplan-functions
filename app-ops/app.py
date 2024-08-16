from chalice import Chalice, Rate
import functools
from urllib import parse

from chalicelib import env_util
from chalicelib import ops

env = env_util.get_env()

app = Chalice(app_name='ops')

def post_fields(request):
    """Return the fields from a POST request."""
    return dict(
        parse.parse_qsl(request.raw_body.decode('UTF-8')))

@app.schedule(Rate(1, unit=Rate.HOURS))
def exercise(event):
    return ops.exercise(event, env)
