import datetime as dt

from django import shortcuts
from django.db.models import Avg, IntegerField, F, Func, ExpressionWrapper
from django.contrib import messages
from django.core import paginator

from . import forms
from . import models
from . import services


def index(request):

    if request.method == 'POST':

        form = forms.AddMatchForm(request.POST)

        if form.is_valid():

            try:
                match_id = services.queue_match(
                    summoner_name=form.cleaned_data['summoner_name'],
                    region=form.cleaned_data['region']
                )
            except Exception as exc:
                messages.error(request, f'{exc.__class__.__name__}: {exc}')
                return shortcuts.redirect('index')

            return shortcuts.redirect('match', match_id=match_id)

        else:
            messages.error(request, 'Bad input')
            return shortcuts.redirect('index')

    # Compute the mean average error (MAE)
    abs_error = ExpressionWrapper(
        Func(F('duration') - F('predicted_duration'), function='ABS'),
        output_field=IntegerField()
    )
    mae = models.Match.objects.exclude(duration__isnull=True)\
                              .annotate(abs_error=abs_error)\
                              .aggregate(Avg('abs_error'))['abs_error__avg']

    # Paginate the matches
    matches = models.Match.objects.prefetch_related('region').order_by('-created_at')
    matches_pag = paginator.Paginator(matches, 15)

    context = {
        'n_queued': models.Match.objects.exclude(rq_job_id__isnull=True).count(),
        'n_fit': models.Match.objects.exclude(rq_job_id__isnull=False).count(),
        'mae': None if mae is None else dt.timedelta(seconds=mae),
        'form': forms.AddMatchForm(),
        'matches': matches_pag.get_page(request.GET.get('page')),
    }

    return shortcuts.render(request, 'index.html', context)


def match(request, match_id):
    match = shortcuts.get_object_or_404(models.Match, pk=match_id)

    import json

    context = {
        'match': match,
        'raw_info': json.dumps(match.raw_info, indent=4)
    }

    if match.has_ended:

        duration = dt.timedelta(seconds=match.duration)
        pred_duration = dt.timedelta(seconds=match.predicted_duration)
        err_duration = abs(duration - pred_duration)
        max_duration = max(duration, pred_duration) + dt.timedelta(minutes=5)

        context = {
            **context,
            'true_bar_percentage': int(100 * duration / max_duration),
            'pred_bar_percentage': int(100 * pred_duration / max_duration),
            'err_duration': err_duration,
            'err_bar_percentage': int(100 * err_duration / max_duration)
        }

    return shortcuts.render(request, 'match.html', context)
