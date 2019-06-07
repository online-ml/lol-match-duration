from django.core.exceptions import *
from requests.exceptions import *


class MatchAlreadyInserted(Exception):

    def __str__(self):
        return 'Match has already been inserted'
