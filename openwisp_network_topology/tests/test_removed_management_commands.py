from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase


class TestRemovedManagementCommands(SimpleTestCase):
    def test_django_netjsongraph_upgrader_is_unavailable(self):
        with self.assertRaisesRegex(CommandError, "Unknown command"):
            call_command("upgrade_from_django_netjsongraph")
