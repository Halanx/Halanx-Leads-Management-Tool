from __future__ import absolute_import, unicode_literals

from celery import Celery, shared_task
from celery.schedules import crontab
from celery.task import periodic_task
from django.conf import settings

from utility.environments import set_settings_module
from utility.logging_utils import sentry_debug_logger
from utility.zohocrm.zohocrm_leads import get_oauthclient_oauth_token_access_token

set_settings_module()

app = Celery('HalanxLeadManagementTool')
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


@periodic_task(run_every=crontab(minute='*/1'))
def run_every_min():
    get_oauthclient_oauth_token_access_token()
