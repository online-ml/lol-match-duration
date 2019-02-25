from django import shortcuts
from django.db.models import Avg, F, Func, ExpressionWrapper, fields
from django.contrib import messages
import django_rq

from . import exceptions
from . import forms
from . import models
from . import services


def index(request):

    if request.method == 'POST':

        # Create a form instance and populate it with data from the request
        form = forms.AddMatchForm(request.POST)

        # Check whether the form is valid
        if form.is_valid():

            try:
                match_id = services.process_match(
                    summoner_name=form.cleaned_data['summoner_name'],
                    region_short_name=form.cleaned_data['region']
                )
            except (exceptions.MatchAlreadyInserted,
                    exceptions.MatchAlreadyEnded,
                    exceptions.SummonerNotFound) as exc:
                messages.error(request, str(exc))
                return shortcuts.redirect('index')

            return shortcuts.redirect('match', match_id=match_id)

        else:
            messages.error(request, 'Bad input')
            return shortcuts.redirect('index')

    duration = ExpressionWrapper(
        Func(F('predicted_ended_at') - F('started_at'), function='ABS'),
        output_field=fields.DurationField()
    )

    agg = models.Match.objects.exclude(ended_at__isnull=True)\
                              .annotate(duration=duration)\
                              .aggregate(Avg('duration'))
    avg_error = agg['duration__avg']

    context = {
        'matches': models.Match.objects.prefetch_related('region').order_by('-created_at'),
        'form': forms.AddMatchForm(),
        'n_ongoing': django_rq.get_scheduler('default').count(),
        'n_predictions': models.Match.objects.exclude(predicted_ended_at__isnull=True).count(),
        'avg_error': str(avg_error).split('.')[0]
    }

    return shortcuts.render(request, 'index.html', context)


def match(request, match_id):
    match = shortcuts.get_object_or_404(models.Match, pk=match_id)
    return shortcuts.render(request, 'match.html', {'match': match})
