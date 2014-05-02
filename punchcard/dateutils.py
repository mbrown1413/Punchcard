
import time
from datetime import date, timedelta

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if not hasattr(settings, "PUNCHCARD_WEEK_START"):
    raise ImproperlyConfigured("settings.PUNCHCARD_WEEK_START is not defined. "
                               "It should be an integer from 0-6, where "
                               "Monday is 0 and Sunday is 6.")
elif settings.PUNCHCARD_WEEK_START not in range(7):
    raise ImproperlyConfigured("settings.PUNCHCARD_WEEK_START is not a valid "
                               "day of the week (0-6).")


def get_partial_week(day=None):
    '''Lists datetime.date objects from the beginning of the week to `day`.

    Does not include days in the week after the specified day. `day` defaults
    to today.

    '''
    if day is None:
        day = date.today()
    week = [day]
    while week[-1].weekday() != settings.PUNCHCARD_WEEK_START:
        week.append(week[-1] + timedelta(days=-1))
    return week[::-1]

def get_week(day=None):
    '''Lists all 7 days of the week that `day` falls on.

    `day` defaults to today.

    '''
    week = get_partial_week(day)
    for i in xrange(7-len(week)):
        week.append(week[-1] + timedelta(days=1))
    return week

def get_recent_weeks(n_weeks, day=None):
    '''Gets `n_weeks` weeks ending with the week that `day` falls on.

    Each week is a list of 7 datetime.date objects. Unless `day` is the last
    day of a week, some days returned will be in the future. `day` defaults to
    today.

    '''
    weeks = [get_week(day)]
    for i in xrange(n_weeks-1):
        week_last_date = weeks[-1][-1] - timedelta(weeks=1)
        # Calling `get_week` here would be slower and unnessesary. Since
        # weeks[-1][-1] will be the last day of a week, `get_partial_week` will
        # always return a full week and get the same result.
        weeks.append(get_partial_week(week_last_date))
    return weeks[::-1]

def date_from_str(s, fmt="%Y-%m-%d"):
    '''
    Returns a datetime.date object from a string and given a time.strptime
    format string.
    '''
    year, month, day = time.strptime(s, fmt)[0:3]
    return date(year, month, day)
