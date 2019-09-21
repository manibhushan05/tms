from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse, HttpResponseRedirect

from api.helper import json_error_response, query_string

"""

GET non-ajax
- on wrong method, 405 text response
- on no auth, redirect to login, with ref-url and error msg
- on success, render html

GET ajax
- on wrong method, 405 json response
- on no auth, 401 json response
- on success, return html if render=true else return json data

POST non-ajax
- on wrong method, 405 text response
- on no auth, 401 PermissionDenied page
- on success, redirect to a certain page with msg

POST ajax
- on wrong method, 405 json response
- on no auth, 401 json response
- on success, return html if render=true else return json data

"""


def no_auth_response(request, msg):
    error_msg = 'Permission Denied: %s' % msg
    if request.is_ajax():
        return json_error_response(error_msg, status=401)
    # is not ajax
    if request.method == 'GET':
        login_url = '/?' + query_string({'from': request.get_full_path(), 'error': error_msg})
        return HttpResponseRedirect(redirect_to=login_url)
    else:
        raise PermissionDenied


def wrong_method_response(request, method_allowed):
    msg = 'method=%s not supported, only %s is allowed' % (request.method, method_allowed)
    if request.is_ajax():
        return json_error_response(msg, status=405)
    else:
        return HttpResponse(msg, status=405)


def authenticated_user(func):
    def inner(request, *args, **kwargs):
        if not request.user:
            return no_auth_response(request, 'no user')
        if not request.user.is_authenticated:
            return no_auth_response(request, 'user not authenticated')
        if not request.user.is_active:
            return no_auth_response(request, 'user inactive')
        return func(request, *args, **kwargs)

    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner


def only_get(func):
    def inner(request, *args, **kwargs):
        if request.method != "GET":
            return wrong_method_response(request, 'GET')
        request.data = request.GET
        return func(request, *args, **kwargs)

    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner


def only_post(func):
    def inner(request, *args, **kwargs):
        if request.method != "POST":
            return wrong_method_response(request, 'POST')
        request.data = request.POST
        return func(request, *args, **kwargs)

    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner


def bad_request(msg=None):
    return HttpResponse('Incorrect use: %s' % (msg or ''), status=400)
