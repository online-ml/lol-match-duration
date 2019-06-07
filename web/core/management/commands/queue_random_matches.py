import datetime as dt
import random

from django.core.management import base
from django.utils import timezone
import django_rq

from core import exceptions
from core import models
from core import api
from core import services


def queue_random_match(max_attempts=20):

    # Shuffle regions
    regions = [r for r in models.Region.objects.all()]
    random.shuffle(regions)

    # Keep track of how many attempts are made
    n_attempts = 0

    for region in regions:

        # Fetch random matches for the current region
        matches = api.fetch_random_matches(region)

        for match in matches:

            try:

                # Try to process the match once per user, because sometimes fetching a particular
                # user bugs out
                for participant in match['participants']:

                    # Stop when too many attempts have been made
                    n_attempts += 1
                    if n_attempts > max_attempts:
                        return

                    try:
                        services.queue_match(participant['summonerName'], region, raise_if_exists=True)
                        return
                    except exceptions.HTTPError:
                        break

            except exceptions.MatchAlreadyInserted:
                continue


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print('Started queuing random matches')

        django_rq.get_scheduler('default').schedule(
            scheduled_time=timezone.now() + dt.timedelta(seconds=60),
            interval=60,
            func=queue_random_match,
            repeat=None  # None means forever
        )
