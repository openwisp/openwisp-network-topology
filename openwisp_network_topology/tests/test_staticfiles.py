import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

from openwisp_utils.tests import capture_stdout


class TestStaticFiles(SimpleTestCase):
    @capture_stdout()
    def test_collectstatic(self):
        """Ensures the staticfile backend used in the installers is happy"""
        app_dir = Path(__file__).resolve().parents[1]
        assets = (
            "css/admin.css",
            "css/src/loading.gif",
            "css/src/netjsongraph-custom.css",
            "css/src/netjsongraph-theme.css",
            "css/src/netjsongraph.css",
            "css/style.css",
            "js/src/netjsongraph.min.js",
        )
        with TemporaryDirectory() as static_root, TemporaryDirectory() as staticfiles_dir:
            staticfiles_dir = Path(staticfiles_dir)
            for asset in assets:
                source = app_dir / "static/netjsongraph" / asset
                destination = staticfiles_dir / "netjsongraph" / asset
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(source, destination)
            with override_settings(
                STATIC_ROOT=static_root,
                STATICFILES_DIRS=[staticfiles_dir],
                STATICFILES_FINDERS=[
                    "django.contrib.staticfiles.finders.FileSystemFinder"
                ],
                STORAGES={
                    "staticfiles": {
                        "BACKEND": "openwisp_utils.storage.CompressStaticFilesStorage"
                    }
                },
            ):
                call_command("collectstatic", interactive=False)
