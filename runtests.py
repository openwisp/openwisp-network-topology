#!/usr/bin/env python

import os
import sys

sys.path.insert(0, 'tests')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openwisp2.settings')

if __name__ == '__main__':
    from django.core.management import execute_from_command_line

    args = sys.argv
    args.insert(1, 'test')
    if not os.environ.get('SAMPLE_APP', False):
        args.insert(2, 'openwisp_network_topology')
        args.insert(3, 'openwisp_network_topology.integrations.device')
    else:
        args.insert(2, 'openwisp2')
execute_from_command_line(args)
