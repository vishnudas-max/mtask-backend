
# import os
# from celery import Celery
# from celery.schedules import crontab

# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# app = Celery('backend')

# # Using a string here means the worker doesn't 
# # have to serialize the configuration object to 
# # child processes. - namespace='CELERY' means all 
# # celery-related configuration keys should 
# # have a `CELERY_` prefix.
# app.config_from_object('django.conf:settings',namespace='CELERY')

# # Load task modules from all registered Django app configs.
# app.autodiscover_tasks()


# #to check email at time intervals 
# CELERY_BEAT_SCHEDULE = {
#     'check-emails-every-5-mins': {
#         'task': 'Order.tasks.run_email_checker',
#         'schedule': crontab(minute='*/1'),
#     },
# }


import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
