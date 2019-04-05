from django import shortcuts
from django.db.models import Avg, F, Func, ExpressionWrapper, fields
from django.contrib import messages
from django.core import paginator

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
                    region=form.cleaned_data['region']
                )
            except Exception as exc:
                messages.error(request, str(exc))
                return shortcuts.redirect('index')

            return shortcuts.redirect('match', match_id=match_id)

        else:
            messages.error(request, 'Bad input')
            return shortcuts.redirect('index')

    duration = ExpressionWrapper(
        Func(F('predicted_ended_at') - F('ended_at'), function='ABS'),
        output_field=fields.DurationField()
    )
    agg = models.Match.objects.exclude(ended_at__isnull=True)\
                              .annotate(duration=duration)\
                              .aggregate(Avg('duration'))

    matches = models.Match.objects.prefetch_related('region').order_by('-created_at')
    matches_pag = paginator.Paginator(matches, 15)

    context = {
        'n_ongoing': models.Match.objects.exclude(rq_job_id__isnull=True).count(),
        'n_fit': models.Match.objects.exclude(rq_job_id__isnull=False).count(),
        'avg_error': agg['duration__avg'],
        'form': forms.AddMatchForm(),
        'matches': matches_pag.get_page(request.GET.get('page')),
    }

    return shortcuts.render(request, 'index.html', context)


def match(request, match_id):
    match = shortcuts.get_object_or_404(models.Match, pk=match_id)
    return shortcuts.render(request, 'match.html', {'match': match})
