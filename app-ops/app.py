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

# We want a rate that is likely to hit every extension at least once a day,
# is unlikely to hit one extension several times in a row, and runs often.
# We assueme that there isn't a problem with resources being used by the calls.
# Every half an hour will handle up to 24 extensions if they are selected
# evenly.
@app.schedule(Rate(30, unit=Rate.MINUTES))
def exercise(event):
    return ops.exercise(event, env)
