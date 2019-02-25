from creme import compose
from creme import preprocessing
from creme import linear_model
from django.core.management import base

from core import models


def extract_cat_features(x):
    return {
        'map_id': x['match']['mapId'],
        'match_mode': x['match']['gameMode'],
        'match_type': x['match']['gameType']
    }


class Command(base.BaseCommand):

    def handle(self, *args, **options):

        print('Adding models')

        cat_feature_extractor = compose.Pipeline([
            ('categories', preprocessing.FuncTransformer(extract_cat_features)),
            ('one_hot', preprocessing.OneHotEncoder())
        ])

        pipeline = compose.Pipeline([
            ('features', cat_feature_extractor),
            ('lin_reg', linear_model.LinearRegression())
        ])

        model = models.Model(
            name='Chateau Mangue',
            pipeline=pipeline
        )
        model.save()
