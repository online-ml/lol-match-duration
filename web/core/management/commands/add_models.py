import statistics

import creme
from creme import compose
from creme import linear_model
from creme import optim
from creme import preprocessing
from django.core.management import base

from core import models


def safe_mean(seq):
    try:
        return statistics.mean(seq)
    except statistics.StatisticsError:
        return 1


def safe_ratio(a, b):
    return (a + 1) / (b + 1)


def get_ranking(participant):

    tiers = {
        tier: i
        for i, tier in enumerate(('IRON', 'BRONZE', 'SILVER', 'GOLD',
                                  'PLATINUM', 'DIAMOND', 'MASTER',
                                  'GRANDMASTER', 'CHALLENGER'))
    }

    ranks = {
        tier: i
        for i, tier in enumerate(('IV', 'III', 'II', 'I'))
    }

    try:
        tier = participant['position'][0]['tier']
        rank = participant['position'][0]['rank']
        return tiers[tier] * len(tiers) + ranks[rank]
    except IndexError:
        return None


def process_match(match):

    # Split the blue side from the red side
    blue_side = [p for p in match['participants'] if p['teamId'] == 100]
    red_side = [p for p in match['participants'] if p['teamId'] == 200]

    # Champion mastery points ratio
    blue_points = safe_mean([p['mastery']['championPoints'] for p in blue_side])
    red_points = safe_mean([p['mastery']['championPoints'] for p in red_side])
    champion_points_ratio = safe_ratio(max(blue_points, red_points), min(blue_points, red_points))

    # Total mastery points ratio
    blue_points = safe_mean([p['total_mastery'] for p in blue_side])
    red_points = safe_mean([p['total_mastery'] for p in red_side])
    total_points_ratio = safe_ratio(max(blue_points, red_points), min(blue_points, red_points))

    # Ranking ratio
    blue_rank = safe_mean(filter(None, [get_ranking(p) for p in blue_side]))
    red_rank = safe_mean(filter(None, [get_ranking(p) for p in red_side]))
    rank_ratio = safe_ratio(max(blue_rank, red_rank), min(blue_rank, red_rank))

    return {
        'mode': match['gameMode'],
        'type': match['gameType'],
        'champion_mastery_points_ratio': champion_points_ratio,
        'total_mastery_points_ratio': total_points_ratio,
        'rank_ratio': rank_ratio
    }


MODELS = {
    'v0': (
        compose.FuncTransformer(process_match) |
        compose.TransformerUnion([
            compose.Whitelister(
                'champion_mastery_points_ratio',
                'total_mastery_points_ratio',
                'rank_ratio',
            ),
            preprocessing.OneHotEncoder('mode', sparse=False),
            preprocessing.OneHotEncoder('type', sparse=False)
        ]) |
        preprocessing.StandardScaler() |
        linear_model.LinearRegression(optim.VanillaSGD(0.005))
    )
}


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print(f'Adding models with creme version {creme.__version__}')

        for name, pipeline in MODELS.items():

            if models.CremeModel.objects.filter(name=name).exists():
                print(f'{name} has already been added')
                continue

            models.CremeModel(name=name, pipeline=pipeline).save()
            print(f'Added {name}')
