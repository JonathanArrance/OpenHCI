BROKER_URL = 'amqp://guest:transcirrus1@172.38.24.10//'
CELERY_RESULT_BACKEND = 'amqp://guest:transcirrus1@172.38.24.10//'

# List of modules to import when celery starts.
CELERY_IMPORTS = ('change_admin_password')

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_TIMEZONE = 'US/Eastern'
CELERY_ENABLE_UTC = True