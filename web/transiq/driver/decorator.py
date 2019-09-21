
from api.helper import json_401_response_no_token, json_401_response_no_auth
from .models import DriverAppUser


def token_required(func):
    def inner(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if auth_header is not None:
            tokens = auth_header.split(' ')
            if len(tokens) == 2 and tokens[0] == 'Token':
                token = tokens[1]
                try:
                    request.driverapp_user = DriverAppUser.objects.get(auth_token=token)
                    return func(request, *args, **kwargs)
                except DriverAppUser.DoesNotExist:
                    return json_401_response_no_token()
        return json_401_response_no_auth()

    inner.__name__ = func.__name__
    inner.__module__ = func.__module__
    inner.__doc__ = func.__doc__
    inner.__dict__ = func.__dict__
    return inner
