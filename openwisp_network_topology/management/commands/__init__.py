from django.core.management.base import BaseCommand


class BaseUpdateCommand(BaseCommand):
    help = 'Update network topology'

    def add_arguments(self, parser):
        parser.add_argument(
            '--label',
            action='store',
            default=None,
            help='Will update topologies containing label',
        )

    def handle(self, *args, **options):
        self.topology_model.update_all(options['label'])


class BaseSaveSnapshotCommand(BaseCommand):
    help = 'Save network topology graph snapshot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--label',
            action='store',
            default=None,
            help='Will save snapshots of topologies containing label',
        )

    def handle(self, *args, **options):
        self.topology_model.save_snapshot_all(options['label'])
