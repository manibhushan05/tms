import time
from django.conf import settings

from transiq.celery import app


def run_async(func_fullname, q=None, args=None, kwargs=None):
    args = args or []
    kwargs = kwargs or {}
    if settings.ENABLE_CELERY:
        if not q:
            execute_async.delay(func_fullname, args=args, kwargs=kwargs)
        else:
            execute_async.apply_async(queue=q, args=[func_fullname], kwargs=dict(args=args, kwargs=kwargs))
    else:
        func = import_func(func_fullname)
        func(*args, **kwargs)


def import_func(func_fullname):
    func_path = func_fullname.split('.')
    func_name = func_path[-1]
    module_path = func_path[:-1]
    module_name = module_path[-1]
    module_parent = __import__('.'.join(module_path))
    module = getattr(module_parent, module_name)
    func = getattr(module, func_name)
    return func


def execute(func_fullname, args, kwargs):
    start = time.time()
    try:
        func = import_func(func_fullname)
        ret = func(*args, **kwargs)
    except Exception as e:
        raise e
    end_time = time.time() - start
    return ret


@app.task(ignore_result=True)
def execute_async(func_fullname, args, kwargs):
    execute(func_fullname, args, kwargs)


