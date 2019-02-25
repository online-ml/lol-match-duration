from django import forms

from . import models


def get_region_choices():
    # you place some logic here
    return [(region.short_name, region.full_name) for region in models.Region.objects.all()]


class AddMatchForm(forms.Form):

    summoner_name = forms.CharField(label='Summoner name', max_length=100)
    region = forms.ChoiceField(label='Region')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['region'].choices = get_region_choices()
