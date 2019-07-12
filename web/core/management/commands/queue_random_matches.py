import datetime as dt
import logging
import random

from django.core.management import base
from django.utils import timezone
import django_rq

from core import exceptions
from core import models
from core import api
from core import services


logger = logging.getLogger(__name__)


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

            # Try to process the match once per user, because sometimes fetching a particular
            # user bugs out
            for participant in match['participants']:

                # Stop when too many attempts have been made
                n_attempts += 1
                if n_attempts > max_attempts:
                    logger.warning('Did not find any match to queue')
                    return

                try:
                    _, already_exists = services.queue_match(
                        summoner_name=participant['summonerName'],
                        region=region,
                        raise_if_exists=True
                    )
                    if already_exists:
                        break
                    return
                except exceptions.HTTPError:
                    logger.error('HTTP error', exc_info=True)
                    break

    logger.warning('Did not find any match to queue')


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print('Started queuing random matches')

        django_rq.get_scheduler('default').schedule(
            scheduled_time=timezone.now() + dt.timedelta(seconds=60),
            interval=60,
            func=queue_random_match,
            repeat=None  # None means forever
        )
