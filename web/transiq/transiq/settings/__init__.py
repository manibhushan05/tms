"""

Settings module organization

defaults.py - contains common settings, rest of settings files import defaults.py

dev.py - contains settings for remote development/staging environment (default)
prod.py - contains settings for remote production environment i.e. live site
local.py - contains settings for your local development machine (ignored by git)

By default, try to load local.py if available else load dev.py

Now we set environment variable `DJANGO_SETTINGS_MODULE=transiq.settings.prod`, in our
apache2 config on the production machine, and as transiq.settings.dev on the remote
development machine (dev is the default so this is not really required).

So,

When running `python manage.py command` settings will default to transiq.settings,
- if we are running this on a local machine, then local.py may be present
- if local.py is present, command is run with settings importing from local.py
- if local.py is not present command is run with settings importing from dev.py

if running manage.py command on a remote machine
- development machine has already been setup to include `DJANGO_SETTINGS_MODULE=transiq.settings.dev`
- production machine has already been setup to include `DJANGO_SETTINGS_MODULE=transiq.settings.prod`
- with the env variables in place execution of manage.py commands on these machines will automatically default to
  respective settings files

NOTE: to import settings use `from django.conf import settings` instead of `from transiq import settings`.
      I have already replaced the existing imports.

"""
try:
    from .local import *
except ImportError:
    from .dev import *
