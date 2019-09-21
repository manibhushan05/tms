from datetime import datetime
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from django.utils.module_loading import import_module


def init_session(session_key):
    """
    Initialize same session as done for ``SessionMiddleware``.
    """
    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore(session_key)


def main():
    """
    Read all available users and all available not expired sessions. Then
    logout from each session.
    """
    now = datetime.now()
    request = HttpRequest()

    sessions = Session.objects.filter(expire_date__gt=now)
    for session in sessions:
        username = session.get_decoded().get('_auth_user_id')
        request.session = init_session(session.session_key)

        logout(request)
        print('    Successfully logout %r user.' % username)

    print('All OK!')


def current_logged_in_users():
    sessions=Session.objects.filter(expire_date__gte=datetime.now())
    for session in sessions:
        user=User.objects.get(id=session.get_decoded()['_auth_user_id'])
        print (user.username,', '.join(user.groups.values_list('name',flat=True)),session.expire_date)

if __name__ == '__main__':
    main()