from django.test import TestCase
from django.urls import reverse
from django_netjsongraph.tests import CreateGraphObjectsMixin
from django_netjsongraph.tests.base.admin import TestAdminMixin

from openwisp_users.tests.utils import TestOrganizationMixin
from openwisp_utils.tests.utils import TestMultitenantAdminMixin

from . import CreateOrgMixin
from ..apps import OpenwispNetworkTopologyConfig as appconfig
from ..models import Link, Node, Topology


class TestAdmin(CreateGraphObjectsMixin, CreateOrgMixin,
                TestAdminMixin, TestCase):
    topology_model = Topology
    link_model = Link
    node_model = Node

    def prefix(self):
        return 'admin:{0}'.format(appconfig.label)

    def setUp(self):
        org = self._create_org()
        t = self._create_topology(organization=org)
        self._create_node(label="node1",
                          addresses="192.168.0.1;",
                          topology=t,
                          organization=org)
        self._create_node(label="node2",
                          addresses="192.168.0.2;",
                          topology=t,
                          organization=org)
        super(TestAdmin, self).setUp()


class TestMultitenantAdmin(CreateGraphObjectsMixin, TestMultitenantAdminMixin,
                           TestOrganizationMixin, TestCase):
    topology_model = Topology
    node_model = Node
    link_model = Link
    operator_permission_filters = [
        {'codename__endswith': 'topology'},
        {'codename__endswith': 'node'},
        {'codename__endswith': 'link'},
    ]

    def _create_multitenancy_test_env(self):
        org1 = self._create_org(name='test1org')
        org2 = self._create_org(name='test2org')
        inactive = self._create_org(name='inactive-org', is_active=False)
        operator = self._create_operator(organizations=[org1, inactive])
        t1 = self._create_topology(label='topology1org', organization=org1)
        t2 = self._create_topology(label='topology2org', organization=org2)
        t3 = self._create_topology(label='topology3org', organization=inactive)
        n11 = self._create_node(label='node1org1', topology=t1, organization=org1)
        n12 = self._create_node(label='node2org1', topology=t1, organization=org1)
        n21 = self._create_node(label='node1org2', topology=t2, organization=org2)
        n22 = self._create_node(label='node2org2', topology=t2, organization=org2)
        n31 = self._create_node(label='node1inactive', topology=t3, organization=inactive)
        n32 = self._create_node(label='node2inactive', topology=t3, organization=inactive)
        l1 = self._create_link(topology=t1,
                               organization=org1,
                               source=n11,
                               target=n12)
        l2 = self._create_link(topology=t2,
                               organization=org2,
                               source=n21,
                               target=n22)
        l3 = self._create_link(topology=t3,
                               organization=inactive,
                               source=n31,
                               target=n32)
        data = dict(t1=t1, t2=t2, t3_inactive=t3,
                    n11=n11, n12=n12, l1=l1,
                    n21=n21, n22=n22, l2=l2,
                    n31=n31, n32=n32, l3_inactive=l3,
                    org1=org1, org2=org2,
                    inactive=inactive,
                    operator=operator)
        return data

    def test_topology_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse('admin:topology_topology_changelist'),
            visible=[data['t1'].label, data['org1'].name],
            hidden=[data['t2'].label, data['org2'].name,
                    data['t3_inactive'].label]
        )

    def test_topology_organization_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse('admin:topology_topology_add'),
            visible=[data['org1'].name],
            hidden=[data['org2'].name, data['inactive']],
            select_widget=True
        )

    def test_node_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse('admin:topology_node_changelist'),
            visible=[data['n11'].label, data['n12'].label, data['org1'].name],
            hidden=[data['n21'].label, data['n22'].label, data['org2'].name,
                    data['n31'].label, data['n32'].label, data['inactive']]
        )

    def test_node_organization_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse('admin:topology_node_add'),
            visible=[data['org1'].name],
            hidden=[data['org2'].name, data['inactive']],
            select_widget=True
        )

    def test_link_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse('admin:topology_link_changelist'),
            visible=[str(data['l1']), data['org1'].name],
            hidden=[str(data['l2']), data['org2'].name,
                    str(data['l3_inactive'])]
        )

    def test_link_organization_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse('admin:topology_link_add'),
            visible=[data['org1'].name],
            hidden=[data['org2'].name, data['inactive']],
            select_widget=True
        )

    def test_node_topology_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse('admin:topology_node_add'),
            visible=[data['t1'].label],
            hidden=[data['t2'].label, data['t3_inactive'].label]
        )

    def test_link_topology_fk_queryset(self):
        data = self._create_multitenancy_test_env()
        self._test_multitenant_admin(
            url=reverse('admin:topology_link_add'),
            visible=[data['t1'].label],
            hidden=[data['t2'].label, data['t3_inactive'].label]
        )

    def test_node_topology_filter(self):
        data = self._create_multitenancy_test_env()
        t_special = self._create_topology(label='special', organization=data['org1'])
        self._test_multitenant_admin(
            url=reverse('admin:topology_node_changelist'),
            visible=[data['t1'].label, t_special.label],
            hidden=[data['t2'].label, data['t3_inactive'].label]
        )

    def test_link_topology_filter(self):
        data = self._create_multitenancy_test_env()
        t_special = self._create_topology(label='special', organization=data['org1'])
        self._test_multitenant_admin(
            url=reverse('admin:topology_link_changelist'),
            visible=[data['t1'].label, t_special.label],
            hidden=[data['t2'].label, data['t3_inactive'].label]
        )
