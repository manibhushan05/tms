
from api.helper import json_error_response


def authenticated_user(func):
    def inner(request, *args, **kwargs):
        if not request.user:
            return json_error_response('no user present', 401)
        if not request.user.is_authenticated:
            return json_error_response('user is not authenticated', 401)
        if not request.user.is_active:
            return json_error_response('user authenticated but inactive', 401)
        if not any(g.name == 'sme' for g in request.user.groups.all()):
            return json_error_response('user not allowed to access this app', 401)
        return func(request, *args, **kwargs)
    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner
