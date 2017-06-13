class CreateMixin(object):
    def _create_topology(self, **kwargs):
        options = dict(label='test-topology',
                       parser='netdiff.NetJsonParser',
                       url='http://127.0.0.1:8000')
        options.update(kwargs)
        t = self.topology_model(**options)
        t.full_clean()
        t.save()
        return t

    def _create_node(self, **kwargs):
        options = dict(label='test-node',
                       addresses='192.168.0.1;')
        options.update(kwargs)
        n = self.node_model(**options)
        n.full_clean()
        n.save()
        return n

    def _create_link(self, **kwargs):
        options = dict(cost='1',
                       cost_text='one',
                       properties={})
        options.update(kwargs)
        l = self.link_model(**options)
        l.full_clean()
        l.save()
        return l
