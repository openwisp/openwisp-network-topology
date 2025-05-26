import os
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import TestCase
from swapper import load_model

User = get_user_model()
Organization = load_model("openwisp_users", "Organization")
Topology = load_model("topology", "Topology")


class TestUpgradeFromDjangoNetjsongraph(TestCase):
    def test_success(self):
        self.assertEqual(Topology.objects.count(), 0)
        commandOutput = StringIO()
        static_path = os.path.join(
            os.path.dirname(__file__), "static", "upgrader_script"
        )
        call_command(
            "upgrade_from_django_netjsongraph", backup=static_path, stdout=commandOutput
        )
        self.assertIn("Migration Process Complete!", commandOutput.getvalue())
        os.remove(os.path.join(static_path, "group_loaded.json"))
        os.remove(os.path.join(static_path, "netjsongraph_loaded.json"))
        os.remove(os.path.join(static_path, "user_loaded.json"))
        self.assertEqual(Topology.objects.count(), 1)
        try:
            Topology.objects.get(label="default")
        except Topology.DoesNotExist:
            self.fail('Topology "default" not created!')
        try:
            user = User.objects.get(username="sample")
            group = Group.objects.filter(user=user).first()
            permissions = Permission.objects.filter(user=user).first()
            self.assertEqual("sample", group.name)
            self.assertEqual("add_logentry", permissions.codename)
        except User.DoesNotExist:
            self.fail('User "sample" not created!')

    def test_files_not_found(self):
        commandOutput = StringIO()
        with self.assertRaises(FileNotFoundError):
            call_command(
                "upgrade_from_django_netjsongraph",
                backup=os.path.join(os.path.dirname(__file__)),
                stdout=commandOutput,
            )

    def test_organization_not_found(self):
        commandOutput = StringIO()
        with self.assertRaises(Organization.DoesNotExist):
            call_command(
                "upgrade_from_django_netjsongraph",
                backup=os.path.join(os.path.dirname(__file__), "static"),
                organization="00000000-0000-0000-0000-000000000000",
                stdout=commandOutput,
            )
