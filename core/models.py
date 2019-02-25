import uuid

from django.db import models
import jsonfield
from picklefield import fields as picklefield


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Model(BaseModel):
    name = models.TextField(unique=True)
    pipeline = picklefield.PickledObjectField()

    class Meta:
        db_table = 't_models'
        verbose_name_plural = 'models'


class Region(BaseModel):
    short_name = models.TextField()
    full_name = models.TextField()
    platform = models.TextField()

    class Meta:
        db_table = 't_regions'
        verbose_name_plural = 'regions'


class Match(BaseModel):
    api_id = models.IntegerField()
    rq_job_id = models.UUIDField(null=True)
    raw_info = jsonfield.JSONField(null=True)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)
    predicted_ended_at = models.DateTimeField(blank=True, null=True)

    region = models.ForeignKey(Region, null=True, on_delete=models.SET_NULL)
    predicted_by = models.ForeignKey(Model, null=True, on_delete=models.SET_NULL)

    @property
    def true_duration(self):
        return (self.ended_at - self.started_at) if self.ended_at else None

    @property
    def predicted_duration(self):
        return (self.predicted_ended_at - self.started_at) if self.predicted_ended_at else None

    @property
    def mode(self):
        if not self.raw_info:
            return None
        try:
            return self.raw_info['match']['gameMode']
        except KeyError:
            return None

    @property
    def type(self):
        if not self.raw_info:
            return None
        try:
            return self.raw_info['match']['gameType']
        except KeyError:
            return None

    class Meta:
        db_table = 't_matches'
        verbose_name_plural = 'matches'
