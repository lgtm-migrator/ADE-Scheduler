import re
from static_data import COURSE_REGEX
from datetime import datetime, timedelta
from ics import Event
from pytz import timezone


# Information extraction functions
def extractCode(code):
    s = re.search(COURSE_REGEX, code, re.IGNORECASE)
    if s:
        return s.group(1)
    else:
        return ''


def extractType(course):
    if re.search(COURSE_REGEX + "-", course, re.IGNORECASE):
        return EventCM
    elif re.search(COURSE_REGEX + "_", course, re.IGNORECASE):
        return EventTP
    elif re.search(COURSE_REGEX + "=E", course, re.IGNORECASE):
        return EventEXAM
    elif re.search(COURSE_REGEX + "=O", course, re.IGNORECASE):
        return EventORAL
    else:
        return EventOTHER


def extractDateTime(date, time, delta):
    # We need to set the timzeone
    tz = timezone('Europe/Brussels')

    t0 = datetime.strptime(date + '-' + time, '%d/%m/%Y-%Hh%M').astimezone(tz)
    s = re.findall(r'[0-9]+', delta)
    if len(s) == 2:
        h = int(s[0])
        m = int(s[1])
    else:
        h = int(s[0])
        m = 0
    dt = timedelta(hours=h, minutes=m)
    t1 = t0 + dt
    return t0, t1, dt


def overlappingTime(event1, event2, onlyOverlap=True, saveCheck=False):
    """
    Compute the overlapping time between two events.
    In option, it can count non-overlap time as negative overlap, in others words, the time between two events.
    Parameters
    ----------
    event1, event2 : ics.Event
        Two events to be compared.
    onlyOverlap : boolean
        If True, only positive overlap is counted.
    saveCheck : boolean
        If True, functions returns 0 if both events are the same.
    Returns
    -------
    c : int
        The total overlapping time, multiplied by the weights, in seconds.
    Raises
    ------
    TypeError
        If event1 or event2 are not subclass of ics.Event.
    """

    if saveCheck and event1 == event2:  # No overlap if same event
        return 0
    if not isinstance(event1, CustomEvent) or not isinstance(event2, CustomEvent):
        raise TypeError

    time = event1.weight * event2.weight * (
                min(event1.end, event2.end) - max(event1.begin, event2.begin)).total_seconds()
    if onlyOverlap:  # Only positive overlap is counted
        return max(time, 0)
    else:
        return time


# Event classes (from ics python package)
class CustomEvent(Event):
    def __init__(self, name, begin, duration, descr, loc, weight=1):
        super().__init__(name=name, begin=begin, duration=duration, description=descr, location=loc)
        self.weight = weight

    def __eq__(self, other):
        if isinstance(other, CustomEvent):
            return (self.name == other.name
                    and self.begin == other.begin
                    and self.duration == other.duration)
        else:
            raise TypeError

    def __ne__(self, other):
        return not self.__eq__(other)

    # Askip il faut rendre CustomEvent hashable pour pouvoir l'ajouter a un calendrier
    # et si on définit pas __hash__() ça fonctionne pas (héritage svp ? :'( )
    def __hash__(self):
        return super().__hash__()

    def getweek(self):
        """
        returns the week of this event in the gregorian calendar, starting at 0 for the first week
        """
        return self.begin.isocalendar()[1] - 1


class EventCM(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'CM: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class EventTP(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'TP: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class EventEXAM(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'EXAM: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class EventORAL(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'ORAL: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)


class EventOTHER(CustomEvent):
    def __init__(self, begin, duration, code, name, professor, loc, weight=1):
        name = 'Other: ' + code + ' - ' + name
        super().__init__(name=name, begin=begin, duration=duration, descr=str(professor), loc=loc, weight=weight)
