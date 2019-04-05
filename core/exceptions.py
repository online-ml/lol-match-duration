class MatchAlreadyInserted(Exception):

    def __str__(self):
        return 'Match has already been inserted'


class MatchAlreadyEnded(Exception):

    def __str__(self):
        return 'Match has already ended'
