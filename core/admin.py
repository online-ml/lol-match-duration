from django.contrib import admin

from . import models


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
admin.site.register(models.Match)
admin.site.register(models.Region, RegionAdmin)
