from django.core.exceptions import PermissionDenied


def authenticated_user_web(func):
    def inner(request, *args, **kwargs):
        if not request.user:
            raise PermissionDenied
        if not request.user.is_authenticated:
            raise PermissionDenied
        if not request.user.is_active:
            raise PermissionDenied
        return func(request, *args, **kwargs)

    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner