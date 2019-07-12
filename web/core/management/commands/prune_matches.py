import datetime as dt

from django.core.management import base
from django.utils import timezone

from core import models
from core import services


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print('Pruning unfinished matches')

        for match in models.Match.objects.exclude(duration__isnull=False):

            if timezone.now() - match.created_at > dt.timedelta(days=7):
                print(f'\tRemoving match {match.id}')
                match.delete()
                continue

            print(f'\tTrying to end match {match.id}')
            services.try_to_end_match(id=match.id)
