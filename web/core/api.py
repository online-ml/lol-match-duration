import random
from urllib.parse import urljoin

from django.conf import settings
import requests

from . import models


__all__ = [
    'fetch_active_match_by_summoner_id',
    'fetch_champion_mastery',
    'fetch_match',
    'fetch_random_matches',
    'fetch_summoner_by_name',
    'fetch_summoner_ranking',
    'fetch_total_champion_mastery',
]


def get_from_api(path, region):
    """Convenience method for making a GET request from Riot's API."""

    if not isinstance(region, models.Region):
        region = models.Region.get(short_name=region)

    url = urljoin(f'https://{region.platform.lower()}.api.riotgames.com', path)

    req = requests.get(url, params={'api_key': settings.RIOT_API_KEY})

    req.raise_for_status()

    return req.json()


def fetch_summoner_by_name(summoner_name, region):
    """Fetchs summoner information using a name."""
    path = f'/lol/summoner/v4/summoners/by-name/{summoner_name}'
    return get_from_api(path, region)


def fetch_active_match_by_summoner_id(summoner_id, region):
    """Fetchs match information using a summoner ID."""
    path = f'/lol/spectator/v4/active-games/by-summoner/{summoner_id}'
    return get_from_api(path, region)


def fetch_match(match_api_id, region):
    """Fetch match information using a match ID."""
    path = f'/lol/match/v4/matches/{match_api_id}'
    return get_from_api(path, region)


def fetch_random_matches(region):
    """Fetch random matches."""
    path = f'/lol/spectator/v4/featured-games'
    matches = get_from_api(path, region)['gameList']
    random.shuffle(matches)
    return matches


def fetch_champion_mastery(summoner_id, champion_id, region):
    """Fetch champion mastery information using a summoner ID."""
    path = f'/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}/by-champion/{champion_id}'
    data = get_from_api(path, region)
    data.pop('championId', None)
    data.pop('summonerId', None)
    return data


def fetch_total_champion_mastery(summoner_id, region):
    """Fetch total champion mastery using a summoner ID."""
    path = f'/lol/champion-mastery/v4/scores/by-summoner/{summoner_id}'
    return get_from_api(path, region)


def fetch_summoner_ranking(summoner_id, region):
    """Fetch ranking information using a summoner ID."""
    path = f'/lol/league/v4/entries/by-summoner/{summoner_id}'
    return get_from_api(path, region)
