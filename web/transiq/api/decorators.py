import json

from api.helper import json_405_response, json_error_response


def no_test(func):
    """
    Use for URLs that do not require testing, use wisely
    """
    def inner(request, *args, **kwargs):
        return func(request, *args, **kwargs)
    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    inner.do_not_test = True
    return inner


def api_get(func):
    def inner(request, *args, **kwargs):
        if request.method != "GET":
            return json_405_response()
        request.data = {}
        return func(request, *args, **kwargs)
    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner


def api_post(func):
    def inner(request, *args, **kwargs):
        if request.method != "POST":
            return json_405_response()
        try:
            request.data = {} if not request.body else json.loads(request.body.decode('utf-8'))
        except ValueError:
            request.data = {}
        return func(request, *args, **kwargs)
    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner


def authenticated_user(func):
    def inner(request, *args, **kwargs):
        if not request.user:
            return json_error_response('no user present', 401)
        if not request.user.is_authenticated:
            return json_error_response('user is not authenticated', 401)
        if not request.user.is_active:
            return json_error_response('user authenticated but inactive', 401)
        return func(request, *args, **kwargs)
    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner
