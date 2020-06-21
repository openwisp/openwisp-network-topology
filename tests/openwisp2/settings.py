import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'openwisp_network_topology.db',
    }
}

SECRET_KEY = '@q4z-^s=mv59#o=uutv4*m=h@)ik4%zp1)-k^_(!_7*x_&+ze$'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'openwisp_utils.admin_theme',
    # all-auth
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # openwisp2 modules
    'openwisp_network_topology',
    'openwisp_users',
    # admin
    'django.contrib.admin',
    # rest framework
    'rest_framework',
    'django_extensions',
    # 'debug_toolbar',
]

AUTH_USER_MODEL = 'openwisp_users.User'
SITE_ID = '1'

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'openwisp_utils.staticfiles.DependencyFinder',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'openwisp2.urls'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'openwisp_utils.loaders.DependencyLoader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'openwisp_utils.admin_theme.context_processor.menu_items',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse',},
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue',},
    },
    'formatters': {
        'simple': {'format': '[%(levelname)s] %(message)s'},
        'verbose': {
            'format': '\n\n[%(levelname)s %(asctime)s] module: %(module)s, process: %(process)d, thread: %(thread)d\n%(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'main_log': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(BASE_DIR, 'error.log'),
            'maxBytes': 5242880.0,
            'backupCount': 3,
        },
    },
    'root': {'level': 'INFO', 'handlers': ['main_log', 'console', 'mail_admins'],},
    'loggers': {'py.warnings': {'handlers': ['console'],}},
}

TEST_RUNNER = 'openwisp_network_topology.tests.utils.LoggingDisabledTestRunner'

EMAIL_PORT = '1025'  # for testing purposes
LOGIN_REDIRECT_URL = 'admin:index'
ACCOUNT_LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL

OPENWISP_ORGANIZATON_USER_ADMIN = True
OPENWISP_ORGANIZATON_OWNER_ADMIN = True


if os.environ.get('SAMPLE_APP', False):
    INSTALLED_APPS.remove('openwisp_network_topology')
    EXTENDED_APPS = ['openwisp_network_topology']
    INSTALLED_APPS.append('openwisp2.sample_network_topology')
    TOPOLOGY_LINK_MODEL = 'sample_network_topology.Link'
    TOPOLOGY_NODE_MODEL = 'sample_network_topology.Node'
    TOPOLOGY_SNAPSHOT_MODEL = 'sample_network_topology.Snapshot'
    TOPOLOGY_TOPOLOGY_MODEL = 'sample_network_topology.Topology'


# local settings must be imported before test runner otherwise they'll be ignored
try:
    from local_settings import *
except ImportError:
    pass
