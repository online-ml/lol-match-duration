import datetime as dt
import logging
import pytz

from django import shortcuts
from django.conf import settings
import django_rq

from . import exceptions
from . import models
from . import api


__all__ = [
    'queue_match',
    'try_to_end_match'
]


logger = logging.getLogger(__name__)


def queue_match(summoner_name, region, raise_if_exists=False):
    """Queues a match and returns it's database ID."""

    # Get the region
    if not isinstance(region, models.Region):
        region = models.Region.objects.get(short_name=region)

    # Fetch summoner information
    summoner = api.fetch_summoner_by_name(summoner_name, region)

    # Fetch current match information from the summoner's ID
    match_info = api.fetch_active_match_by_summoner_id(summoner['id'], region)

    # Check if the match has ended or not
    if 'gameDuration' in match_info:
        raise ValueError('The match has already ended')

    # Check if the match has already been inserted
    try:
        match = models.Match.objects.get(api_id=match_info['gameId'], region=region)
        return match.id, True
    except exceptions.ObjectDoesNotExist:
        pass

    # Add extra information
    for i, participant in enumerate(match_info['participants']):

        # Champion mastery for the current champion
        match_info['participants'][i]['mastery'] = api.fetch_champion_mastery(
            summoner_id=participant['summonerId'],
            champion_id=participant['championId'],
            region=region
        )

        # Total champion mastery score, which is the sum of individual champion mastery levels
        match_info['participants'][i]['total_mastery'] = api.fetch_total_champion_mastery(
            summoner_id=participant['summonerId'],
            region=region
        )

        # Current ranked position
        match_info['participants'][i]['position'] = api.fetch_summoner_ranking(
            summoner_id=participant['summonerId'],
            region=region
        )

    # The game length is the current amount of time spent in the game, we don't need it
    match_info.pop('gameLength', None)
    match_info.pop('observers', None)
    match_info.pop('platformId', None)

    # Build the Match instance
    match = models.Match(
        api_id=str(match_info['gameId']),
        region=region,
        raw_info=match_info,
        started_at=pytz.utc.localize(dt.datetime.fromtimestamp(match_info['gameStartTime'] / 1000))
    )

    # Predict the match duration
    ok = False
    while not ok:
        duration, ok = models.CremeModel.objects.get(name=settings.MODEL_NAME)\
                             .predict_one(match.raw_info)
        if not ok:
            logger.warning('Optimistic logging failed when predicting')

    # Clamp the prediction we know the min/max time of a match
    min_duration = dt.timedelta(minutes=10 if match.mode == 'ARAM' else 15).seconds
    max_duration = dt.timedelta(hours=3).seconds
    predicted_duration = min(max(duration, min_duration), max_duration)

    # Save the model to get an ID that we can give to RQ
    match.predicted_duration = int(predicted_duration)
    match.save()

    # Schedule a job that calls try_to_end_match until the game ends
    scheduler = django_rq.get_scheduler('default')
    job = scheduler.schedule(
        scheduled_time=match.started_at + dt.timedelta(minutes=15),
        interval=60,
        func=try_to_end_match,
        kwargs={'id': match.id},
        repeat=None  # None means forever
    )
    match.rq_job_id = job.get_id()
    match.save()

    return match.id, False


def try_to_end_match(id):

    match = models.Match.objects.get(id=id)
    region = match.region

    # Fetch the match information
    try:
        match_info = api.fetch_match(match_api_id=match.api_id, region=region)
    except exceptions.HTTPError:
        return

    # Get the duration in seconds
    duration = match_info.get('gameDuration')

    # Can't do anything if the game hasn't ended yet
    if duration is None:
        return

    # Set the match's end time
    match.duration = int(duration)

    # Set the winning team ID
    if match_info['teams'][0]['win'] == 'Win':
        match.winning_team_id = match_info['teams'][0]['teamId']
    else:
        match.winning_team_id = match_info['teams'][1]['teamId']

    ok = False
    while not ok:
        ok = models.CremeModel.objects.get(name=settings.MODEL_NAME)\
                   .fit_one(match.raw_info, match.duration)
        if not ok:
            logger.warning('Optimistic logging failed when fitting')

    # Stop polling the match
    scheduler = django_rq.get_scheduler('default')
    scheduler.cancel(match.rq_job_id)
    match.rq_job_id = None
    match.save()
