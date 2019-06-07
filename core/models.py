import uuid

from django.db import models
from django.contrib.postgres.fields import JSONField
from picklefield import fields as picklefield


__all__ = [
    'CremeModel',
    'Match',
    'Region'
]


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CremeModel(BaseModel):
    name = models.TextField(unique=True)
    pipeline = picklefield.PickledObjectField()

    class Meta:
        db_table = 't_creme_models'
        verbose_name_plural = 'models'

    def fit_one(self, x, y):
        """Attempts to update the model and indicates if the update was successful or not."""
        return CremeModel.objects\
                         .filter(id=self.id, updated_at=self.updated_at)\
                         .update(pipeline=self.pipeline.fit_one(x, y)) > 0

    def predict_one(self, x):
        return (
            self.pipeline.predict_one(x),
            CremeModel.objects
                      .filter(id=self.id, updated_at=self.updated_at)
                      .update(pipeline=self.pipeline) > 0
        )

    def __str__(self):
        return f'Model {self.name}'


class Region(BaseModel):
    short_name = models.TextField()
    full_name = models.TextField()
    platform = models.TextField()

    class Meta:
        db_table = 't_regions'
        verbose_name_plural = 'regions'

    def __str__(self):
        return f'{self.full_name} ({self.short_name})'


class Match(BaseModel):
    api_id = models.TextField(unique=True)
    rq_job_id = models.UUIDField(null=True)
    raw_info = JSONField(null=True)
    started_at = models.DateTimeField()
    duration = models.PositiveSmallIntegerField(null=True)
    predicted_duration = models.PositiveSmallIntegerField(null=True)
    winning_team_id = models.PositiveSmallIntegerField(null=True)

    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL)
    predicted_by = models.ForeignKey(CremeModel, null=True, on_delete=models.SET_NULL)

    @property
    def absolute_error(self):
        if self.duration and self.predicted_duration:
            return abs(self.duration - self.predicted_duration)
        return None

    @property
    def has_ended(self):
        return self.duration is not None

    @property
    def mode(self):
        if not self.raw_info:
            return None
        try:
            return self.raw_info['gameMode']
        except KeyError:
            return None

    @property
    def type(self):
        if not self.raw_info:
            return None
        try:
            return self.raw_info['gameType']
        except KeyError:
            return None

    class Meta:
        db_table = 't_matches'
        verbose_name_plural = 'matches'

    def __str__(self):
        return f'Match {self.api_id}'
