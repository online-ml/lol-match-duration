import datetime as dt

from django import timezone
from django.core.management import base
import django_rq

from core import services


def poll_matches():
    match = services.fetch_random_match()
    services.process_match(match)


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print('Polling matches')

        scheduler = django_rq.get_scheduler('default')
        job = scheduler.schedule(
            scheduled_time=timezone.now() + dt.timedelta(seconds=60),
            interval=60 * 5,
            func=poll_matches,
            repeat=None  # None means forever
        )
