import transcirrus.common.config as config
BROKER_URL = 'amqp://guest:transcirrus1@172.24.24.10//'
CELERY_RESULT_BACKEND = 'amqp://guest:%s@172.24.24.10//'%(config.MASTER_PWD)

# List of modules to import when celery starts.
CELERY_IMPORTS = ('change_admin_password','reset_factory_defaults','rollback_setup','build_complete_project','destroy_project')

CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_TIMEZONE = 'US/Eastern'
CELERY_ENABLE_UTC = True
