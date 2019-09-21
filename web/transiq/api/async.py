import multiprocessing

import time
from django.conf import settings

from api.models import KeyValueStore
from api.tasks import execute_async


def run(func, q=None, args=None, kwargs=None):
    args = args or []
    kwargs = kwargs or {}
    func_fullname = '.'.join([func.__module__, func.__name__])
    if settings.ENABLE_CELERY:
        if not q:
            execute_async.delay(func_fullname, args=args, kwargs=kwargs)
        else:
            execute_async.apply_async(queue=q, args=[func_fullname], kwargs=dict(args=args, kwargs=kwargs))
    else:
        run_mp(func, args=args, kwargs=kwargs)


def run_mp(func, args, kwargs):
    process = multiprocessing.Process(name='mp_%s' % time.time(), target=func, args=args, kwargs=kwargs)
    process.daemon = True
    process.start()


def test_func():
    KeyValueStore.set('new', 'me')


def test():
    run(test_func)


