import datetime as dt

from django import template


register = template.Library()


@register.filter()
def secondsduration(seconds):
    return dt.timedelta(seconds=seconds)


@register.filter
def naturalduration(timedelta):
    """Converts a timedelta to a detailed human readable string.

    This implementation is not generic at all, it's specific to our purposes. It's surprising that
    Django doesn't support this out of the box.

    """

    hours = timedelta.seconds // 3600
    if hours:
        timedelta -= dt.timedelta(hours=hours)

    minutes = timedelta.seconds // 60
    if minutes:
        timedelta -= dt.timedelta(minutes=minutes)

    seconds = timedelta.seconds
    if seconds:
        timedelta -= dt.timedelta(seconds=seconds)

    human = ''

    if hours > 0:
        human += f'{hours} hour' + ('s' if hours > 1 else '')

    if minutes > 0:
        if human:
            human += ', '
        human += f'{minutes} minute' + ('s' if minutes > 1 else '')

    if seconds > 0:
        if human:
            human += ', '
        human += f'{seconds} second' + ('s' if seconds > 1 else '')

    return human
