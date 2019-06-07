import csv

from django.contrib import admin
from django.http import HttpResponse

from . import models


class ExportCSVMixin:

    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta.verbose_name_plural)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = 'Export selected'


@admin.register(models.Match)
class MatchAdmin(admin.ModelAdmin, ExportCSVMixin):

    list_display = ('id', 'api_id', 'rq_job_id', 'created_at', 'started_at', 'duration',
                    'predicted_duration', 'winning_team_id', 'region')
    list_display_link = ('id',)
    actions = ['export_as_csv']


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):

    def n_queued(obj):
        return obj.match_set.exclude(duration__isnull=False).count()
    n_queued.short_description = 'Number of queued matches'

    def n_finished(obj):
        return obj.match_set.exclude(duration__isnull=True).count()
    n_finished.short_description = 'Number of finished matches'

    list_display = ('short_name', 'full_name', 'platform', n_queued, n_finished)
    list_per_page = 20


admin.site.register(models.CremeModel)
