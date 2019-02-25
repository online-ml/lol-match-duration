"""
- https://developer.riotgames.com/regional-endpoints.html
- https://support.riotgames.com/hc/en-us/articles/201751684-League-of-Legends-Servers
"""
import collections

from django.core.management import base

from core import models


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print('Adding regions')

        Region = collections.namedtuple('Region', 'short_name full_name platform')

        regions = [
            Region('BR', 'Brazil', 'BR1'),
            Region('EUNE', 'Europe Nordic & East', 'EUN1'),
            Region('EUW', 'Europe West', 'EUW1'),
            Region('JP', 'Japan', 'JP1'),
            Region('KR', 'Korea', 'KR'),
            Region('LAN', 'Latin America North', 'LA1'),
            Region('LAS', 'Latin America South', 'LA2'),
            Region('NA', 'North America', 'NA1'),
            Region('OCE', 'Oceania', 'OC1'),
            Region('TR', 'Turkey', 'TR1'),
            Region('RU', 'Russia', 'RU1'),
        ]

        for region in regions:
            models.Region(**region._asdict()).save()
