class MatchAlreadyInserted(Exception):

    def __str__(self):
        return 'Match has already been inserted'


class MatchAlreadyEnded(Exception):

    def __str__(self):
        return 'Match has already ended'


class SummonerNotFound(Exception):

    def __str__(self):
        return "Summoner can't be found"
