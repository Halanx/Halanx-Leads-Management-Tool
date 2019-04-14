import os

PRODUCTION = 'production'
TESTING = 'testing'
DEVELOPMENT = 'development'


def set_settings_module():
    if os.environ.get('ENVIRONMENT') == PRODUCTION:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HalanxLeadManagementTool.settings.production')
    elif os.environ.get('ENVIRONMENT') == TESTING:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HalanxLeadManagementTool.settings.testing')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HalanxLeadManagementTool.settings.development')
