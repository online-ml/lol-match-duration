import copy
import statistics

import creme
from creme import compose
from creme import dummy
from creme import linear_model
from creme import optim
from creme import preprocessing
from creme import stats
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


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print(f'Adding models with creme version {creme.__version__}')

        pipeline = compose.FuncTransformer(process_match)
        pipeline |= compose.TransformerUnion([
            compose.Whitelister([
                'mode',
                'champion_mastery_points_ratio',
                'total_mastery_points_ratio',
                'rank_ratio',
            ]),
            preprocessing.OneHotEncoder('type')
        ])
        optimizer = optim.VanillaSGD(0.005)
        lin_reg = preprocessing.StandardScaler() | linear_model.LinearRegression(optimizer)
        pipeline |= compose.SplitRegressor(
            on='mode',
            models={
                'ARAM': copy.deepcopy(lin_reg),
                'CLASSIC': copy.deepcopy(lin_reg)
            },
            default_model=dummy.StatisticRegressor(stats.Mean())
        )

        model = models.Model(
            name='v0',
            pipeline=pipeline
        )
        model.save()
