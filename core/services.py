import datetime as dt
import pytz
import random
from urllib.parse import urljoin

from django import shortcuts
from django.db import transaction
from django.conf import settings
import django_rq
import requests

from . import exceptions
from . import models


def get_from_riot_api(path, region, raise_with_404=None):
    """Convenience method for making a GET request from Riot's API."""

    if isinstance(region, str):
        region = models.Region.get(short_name=region)

    url = urljoin(f'https://{region.platform.lower()}.api.riotgames.com', path)

    req = requests.get(url, params={'api_key': settings.RIOT_API_KEY})

    if not req.ok:
        if raise_with_404 and req.status_code == 404:
            raise raise_with_404
        raise RuntimeError(req.json())

    return req.json()


def fetch_summoner_by_name(summoner_name, region):
    """Fetchs summoner information using a name."""
    path = f'/lol/summoner/v4/summoners/by-name/{summoner_name}'
    return get_from_riot_api(path, region, exceptions.SummonerNotFound())


def fetch_active_match_by_summoner_id(summoner_id, region):
    """Fetchs match information using a summoner ID."""
    path = f'/lol/spectator/v4/active-games/by-summoner/{summoner_id}'
    return get_from_riot_api(path, region)


def fetch_match(match_api_id, region):
    """Fetch match information using a match ID."""
    path = f'/lol/match/v4/matches/{match_api_id}'
    return get_from_riot_api(path, region)


def fetch_random_match(region):
    """Fetch a random match."""
    path = f'/lol/spectator/v4/featured-games'
    matches = get_from_riot_api(path, region)
    return random.choice(matches['gameList'])


def fetch_champion_mastery(summoner_id, champion_id, region):
    """Fetch champion mastery information using a summoner ID."""
    path = f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}/by-champion/{champion_id}'
    return get_from_riot_api(path, region)


def fetch_total_champion_mastery_score(summoner_id, region):
    """Fetch champion mastery information using a summoner ID."""
    path = f'/lol/champion-mastery/v4/scores/by-summoner/{summoner_id}'
    return get_from_riot_api(path, region)


def process_match(summoner_name, region_short_name, raise_has_ended=True):
    """Builds and returns a Game instance using a summoner name and a region."""

    # Get the region
    region = models.Region.objects.get(short_name=region_short_name)

    # Fetch summoner information
    summoner = fetch_summoner_by_name(summoner_name, region)

    # Fetch current match information from the summoner's ID
    match_info = fetch_active_match_by_summoner_id(summoner['id'], region)

    # Check if the match has ended or not
    if raise_has_ended and match_info.get('gameDuration', -1) > 0:
        raise exceptions.MatchAlreadyEnded()

    # Check if the match has already been inserted
    if models.Match.objects.filter(api_id=match_info['gameId'], region=region).exists():
        raise exceptions.MatchAlreadyInserted()

    # Build the Match instance
    match = models.Match(
        api_id=match_info['gameId'],
        region=region,
        raw_info={
            'match': match_info
        },
        started_at=pytz.utc.localize(dt.datetime.fromtimestamp(match_info['gameStartTime'] / 1000))
    )

    # Predict the match duration
    model = models.Model.objects.get(name='Chateau Mangue')
    duration = model.pipeline.predict_one(match.raw_info)
    match.predicted_ended_at = match.started_at + dt.timedelta(seconds=duration)
    match.predicted_by = model
    match.save()

    # Schedule a job that calls try_to_end_match until the game ends
    scheduler = django_rq.get_scheduler('default')
    job = scheduler.schedule(
        scheduled_time=match.started_at + dt.timedelta(minutes=15),
        interval=60,
        func=try_to_end_match,
        kwargs={'match_id': match.id},
        repeat=None  # None means forever
    )
    match.rq_job_id = job.get_id()
    match.save()

    return match.id


def try_to_end_match(match_id):

    match = models.Match.objects.get(id=match_id)
    region = match.region

    # Fetch the match information
    path = f'/lol/match/v4/matches/{match.api_id}'
    url = urljoin(f'https://{region.platform.lower()}.api.riotgames.com', path)
    req = requests.get(url, params={'api_key': settings.RIOT_API_KEY})

    # Matches that haven't finished yet return a 404
    if req.status_code == 404:
        return

    if not req.ok:
        raise RuntimeError(req.json())

    match_info = req.json()
    duration = match_info.get('gameDuration', -1)

    if duration < 0:
        return

    # Set the match's end time
    match = shortcuts.get_object_or_404(models.Match, id=match_id, region=region)
    match.ended_at = match.started_at + dt.timedelta(seconds=duration)

    # https://medium.com/@hakibenita/how-to-manage-concurrency-in-django-models-b240fed4ee2
    with transaction.atomic():
        # Update the online learning model
        model = models.Model.objects.get(id=match.predicted_by.id)
        model.pipeline.fit_one(match.raw_info, match.true_duration.seconds)
        model.save()

    # Stop polling the match
    scheduler = django_rq.get_scheduler('default')
    scheduler.cancel(match.rq_job_id)
    match.rq_job_id = None
    match.save()
