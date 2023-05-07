
def log(msg):
    print(msg)

def twiml_response(twiml):
    return {
        "headers": {"Content-Type": "text/xml"},
        "statusCode": 200,
        "body": str(twiml)}

def function_url(context, function_name):
    """Return the URL for another function in this package and namespace."""
    package = 'dialplans'
    return context.api_host + '/api/v1/web/' + context.namespace + '/' + package + '/' + function_name
