def log(msg):
    print(msg)

def log_request(request):
    msg = 'request '
    msg += 'query_params:{} '.format(request.query_params)
    msg += 'uri_params:{} '.format(request.uri_params)
    msg += 'path:{} '.format(request.path)
    msg += 'raw_body:{}'.format(request.raw_body)
    log(msg)

def log_response(response):
    msg = 'response '
    msg += 'status_code:{} '.format(response.status_code)
    msg += 'body:{}'.format(response.body)
    log(msg)
