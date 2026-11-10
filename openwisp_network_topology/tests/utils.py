import logging
import os

import swapper

from openwisp_utils.tests import TimeLoggingTestRunner

Organization = swapper.load_model("openwisp_users", "Organization")


class CreateOrgMixin(object):
    def _create_org(self, **kwargs):
        options = dict(name="test-organization")
        options.update(kwargs)
        org = Organization(**options)
        org.save()
        return org


class CreateGraphObjectsMixin(object):
    def _create_topology(self, **kwargs):
        options = dict(
            label="TestNetwork",
            parser="netdiff.OlsrParser",
            strategy="fetch",
            url="http://127.0.0.1:9090",
            protocol="OLSR",
            version="0.8",
            metric="ETX",
            created="2017-07-10T20:02:52.483Z",
            modified="2015-07-14T20:02:52.483Z",
        )
        options.update(kwargs)
        t = self.topology_model(**options)
        t.full_clean()
        t.save()
        return t

    def _create_node(self, **kwargs):
        options = dict(
            label="TestNode",
            addresses=["192.168.0.1"],
            created="2017-07-10T20:02:52.483Z",
            modified="2017-07-14T20:02:52.483Z",
            properties={},
        )
        options.update(kwargs)
        n = self.node_model(**options)
        n.full_clean()
        n.save()
        return n

    def _create_link(self, **kwargs):
        options = dict(cost="1", cost_text="one", properties={})
        options.update(kwargs)
        link = self.link_model(**options)
        link.full_clean()
        link.save()
        return link

    def _create_disabled_org_objects(self):
        org = self._create_org(name="disabled-org")
        topology = self._create_topology(label="disabled-topology", organization=org)
        node1 = self._create_node(
            label="disabled-node1",
            addresses=["192.168.10.1"],
            topology=topology,
            organization=org,
        )
        node2 = self._create_node(
            label="disabled-node2",
            addresses=["192.168.10.2"],
            topology=topology,
            organization=org,
        )
        link = self._create_link(
            topology=topology, organization=org, source=node1, target=node2
        )
        org.is_active = False
        org.save(update_fields=["is_active"])
        return org, topology, node1, link


class LoggingDisabledTestRunner(TimeLoggingTestRunner):
    def run_tests(self, test_labels, **kwargs):
        # disable logging below CRITICAL while testing
        logging.disable(logging.CRITICAL)
        return super().run_tests(test_labels, **kwargs)


class UnpublishMixin(object):
    def _unpublish(self):
        t = self.topology_model.objects.first()
        t.published = False
        t.save()


class LoadMixin(object):
    def _load(self, file):
        d = os.path.dirname(os.path.abspath(__file__))
        return open(os.path.join(d, file)).read()
