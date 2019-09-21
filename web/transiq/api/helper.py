import json
import random
import string
import urllib.request


from django.http.response import HttpResponse

EMP_GROUP1 = 'emp_group1'
EMP_GROUP2 = 'emp_group2'
EMP_GROUP3 = 'emp_group3'  # type: str
EMP_GROUP4 = 'emp_group4'


def query_string(data):
    return '&'.join(['%s=%s' % (urllib.request.quote(k), urllib.request.quote(v)) for k, v in data.items()])


def zip_response(byte_io, zip_filename):
    resp = HttpResponse(byte_io.getvalue(), content_type='application/x-zip-compressed')
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp


def json_400_json_error():
    return json_error_response('could not decode json', 400)


def json_400_incorrect_use():
    return json_error_response('incorrect use of api', 400)


def json_401_response_no_token():
    return json_error_response('token required', 401)


def json_401_response_no_auth():
    return json_error_response('authentication required', 401)


def json_401_wrong_credentials():
    return json_error_response('username or password incorrect', 401)


def json_401_inactive_user():
    return json_error_response('user account disabled or inactive', 401)


def json_405_response():
    return json_error_response('incorrect http method', 405)


def json_error_response(msg, status):
    return json_response({'status': 'error', 'msg': '%s, %s: %s' % (status, standard_error_msg(status), msg)},
                         status=status)


def standard_error_msg(status):
    return {
        400: 'Bad Request',
        404: 'Not Found',
        405: 'Unsupported Method',
        403: 'Forbidden',
        401: 'Authentication Required',
        409: 'Conflict',
    }.get(status, 'Unknown Error')


def json_success_response(msg, **kwargs):
    resp_data = {'status': 'success', 'msg': msg}
    if 'status' in kwargs or 'msg' in kwargs:
        raise AssertionError('This is NOT how you use this function! call Shobhit for more info')
    for key, val in kwargs.items():
        resp_data[key] = val
    return json_response(resp_data, status=200)


def json_response(data, **kwargs):
    return HttpResponse(json.dumps(data), content_type='application/json', **kwargs)


def generate_random_password(password_length):
    try:
        return ''.join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase + '@#&*%$') for _ in
            range(password_length))
    except TypeError:
        return ''.join(
            random.choice(string.ascii_uppercase + string.digits + string.ascii_lowercase + '@#&*%$') for _ in
            range(10))
