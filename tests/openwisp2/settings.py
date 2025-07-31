import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTING = "test" in sys.argv


DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "openwisp_utils.db.backends.spatialite",
        "NAME": os.path.join(BASE_DIR, "openwisp_network_topology.db"),
    }
}

if TESTING and "--exclude-tag=no_parallel" not in sys.argv:
    DATABASES["default"]["TEST"] = {
        "NAME": os.path.join(BASE_DIR, "openwisp_network_topology_tests.db"),
    }

SECRET_KEY = "@q4z-^s=mv59#o=uutv4*m=h@)ik4%zp1)-k^_(!_7*x_&+ze$"

INSTALLED_APPS = [
    "daphne",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "openwisp_utils.admin_theme",
    # all-auth
    "django.contrib.sites",
    "openwisp_users.accounts",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # controller  (needed to test integration)
    "openwisp_controller.pki",
    "openwisp_controller.config",
    "openwisp_controller.connection",
    "openwisp_controller.geo",
    "openwisp_notifications",
    "openwisp_ipam",
    "reversion",
    "sortedm2m",
    "flat_json_widget",
    # network topology
    "openwisp_network_topology",
    "openwisp_network_topology.integrations.device",
    "openwisp_users",
    # admin
    "import_export",
    "admin_auto_filters",
    "django.contrib.admin",
    "django.forms",
    # rest framework
    "rest_framework",
    "drf_yasg",
    "django_filters",
    "rest_framework.authtoken",
    "django_extensions",
    # 'debug_toolbar',
    # channels
    "channels",
]


EXTENDED_APPS = ["django_x509", "django_loci"]

AUTH_USER_MODEL = "openwisp_users.User"
SITE_ID = 1

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "openwisp_utils.staticfiles.DependencyFinder",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = "openwisp2.urls"

ASGI_APPLICATION = "openwisp2.asgi.application"

# Needed to test UI updates via websockets
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": ["redis://localhost/9"]},
    }
}
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = "/static/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
                "openwisp_utils.loaders.DependencyLoader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "openwisp_utils.admin_theme.context_processor.menu_groups",
            ],
        },
    }
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"},
        "require_debug_true": {"()": "django.utils.log.RequireDebugTrue"},
    },
    "formatters": {
        "simple": {"format": "[%(levelname)s] %(message)s"},
        "verbose": {
            "format": "\n\n[%(levelname)s %(asctime)s] module: %(module)s, process: %(process)d, thread: %(thread)d\n%(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "filters": ["require_debug_true"],
            "formatter": "simple",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "main_log": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "verbose",
            "filename": os.path.join(BASE_DIR, "error.log"),
            "maxBytes": 5242880.0,
            "backupCount": 3,
        },
    },
    "root": {"level": "INFO", "handlers": ["main_log", "console", "mail_admins"]},
    "loggers": {"py.warnings": {"handlers": ["console"]}},
}

TEST_RUNNER = "openwisp_network_topology.tests.utils.LoggingDisabledTestRunner"

# during development only
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

LOGIN_REDIRECT_URL = "admin:index"
ACCOUNT_LOGOUT_REDIRECT_URL = LOGIN_REDIRECT_URL

OPENWISP_ORGANIZATION_USER_ADMIN = True
OPENWISP_ORGANIZATION_OWNER_ADMIN = True
OPENWISP_USERS_AUTH_API = True

# Note that the following celery settings
# are intended only for development purposes
# and should not be used in a production environment
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"

if not TESTING and any(["shell" in sys.argv, "shell_plus" in sys.argv]):
    LOGGING.update(
        {
            "loggers": {
                "django.db.backends": {
                    "handlers": ["console"],
                    "level": "DEBUG",
                    "propagate": False,
                }
            }
        }
    )

# Avoid adding unnecessary dependency to speedup tests.
if not TESTING or (TESTING and os.environ.get("WIFI_MESH", False)):
    OPENWISP_NETWORK_TOPOLOGY_WIFI_MESH_INTEGRATION = True
    openwisp_ipam_index = INSTALLED_APPS.index("openwisp_ipam")
    INSTALLED_APPS.insert(openwisp_ipam_index, "leaflet")
    INSTALLED_APPS.insert(openwisp_ipam_index, "nested_admin")
    INSTALLED_APPS.insert(openwisp_ipam_index, "openwisp_monitoring.check")
    INSTALLED_APPS.insert(openwisp_ipam_index, "openwisp_monitoring.device")
    INSTALLED_APPS.insert(openwisp_ipam_index, "openwisp_monitoring.monitoring")
    TIMESERIES_DATABASE = {
        "BACKEND": "openwisp_monitoring.db.backends.influxdb",
        "USER": "openwisp",
        "PASSWORD": "openwisp",
        "NAME": "openwisp2",
        "HOST": os.getenv("INFLUXDB_HOST", "localhost"),
        "PORT": "8086",
    }
    OPENWISP_MONITORING_MAC_VENDOR_DETECTION = False
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://localhost/9",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
        }
    }

if os.environ.get("SAMPLE_APP", False):
    INSTALLED_APPS.remove("openwisp_network_topology")
    INSTALLED_APPS.remove("openwisp_network_topology.integrations.device")
    EXTENDED_APPS.append("openwisp_network_topology")
    INSTALLED_APPS += [
        "openwisp2.sample_network_topology",
        "openwisp2.sample_integration_device",
    ]
    TOPOLOGY_LINK_MODEL = "sample_network_topology.Link"
    TOPOLOGY_NODE_MODEL = "sample_network_topology.Node"
    TOPOLOGY_SNAPSHOT_MODEL = "sample_network_topology.Snapshot"
    TOPOLOGY_TOPOLOGY_MODEL = "sample_network_topology.Topology"
    TOPOLOGY_DEVICE_DEVICENODE_MODEL = "sample_integration_device.DeviceNode"
    TOPOLOGY_DEVICE_WIFIMESH_MODEL = "sample_integration_device.WifiMesh"

# local settings must be imported before test runner otherwise they'll be ignored
try:
    from .local_settings import *
except ImportError:
    pass
