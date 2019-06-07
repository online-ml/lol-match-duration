from django.core.management import base

from core import models
from core import services


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print('Pruning unfinished matches')

        for match in models.Match.objects.exclude(duration__isnull=False):
            print(f'\tChecking match {match.id}')
            services.try_to_end_match(id=match.id)
