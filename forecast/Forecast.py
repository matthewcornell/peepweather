import datetime
import logging

from forecast.WeatherGovSource import WeatherGovSource


logger = logging.getLogger(__name__)


class Forecast:
    """
    Computes a forecast using WeatherGovSource and its sequence of Hours.
    """

    # default ranges (AKA a 'range dict'). see range-documentation.txt for detail
    PARAM_RANGE_STEPS_DEFAULT = {'precip': [10, 30],  # H->M, M->L
                                 'temp': [35, 59, 89, 100],  # L->, M->H, H->, M->L
                                 'wind': [8, 12],  # H->M, M->L
                                 'clouds': [33, 66],  # H->M, M->L
    }


    def __init__(self, location, rangeDict=None):
        """
        :param location: Location to get the forecast for
        :param rangeDict: optional as in PARAM_RANGE_STEPS_DEFAULT. uses that default if not passed
        :return:
        """
        # check rangeDict
        def isIntList(theList):
            return isinstance(theList, list) and len(theList) != 0 and \
                   all(map(lambda val: isinstance(val, int), theList))


        def isSortedList(theList):
            return theList == sorted(theList)


        if rangeDict:
            if not isinstance(rangeDict, dict):
                raise ValueError("rangeDict is not a dict: {}".format(rangeDict))
            if set(rangeDict.keys()) != {'precip', 'temp', 'wind', 'clouds'}:
                raise ValueError("rangeDict is missing a parameter key: {}".format(rangeDict))
            if not all(map(isIntList, rangeDict.values())):
                raise ValueError("rangeDict values were not all lists of ints: {}".format(rangeDict))
            if len(rangeDict['precip']) != 2 or len(rangeDict['wind']) != 2 or len(rangeDict['clouds']) != 2:
                raise ValueError("rangeDict precip, wind, or clouds is not a list of two ints: {}".format(rangeDict))
            if len(rangeDict['temp']) != 4:
                raise ValueError("rangeDict temp is not a list of four ints".format(rangeDict))
            if not all(map(isSortedList, rangeDict.values())):
                raise ValueError("rangeDict values were not all sorted: {}".format(rangeDict))

            self.rangeDict = rangeDict
        else:
            self.rangeDict = Forecast.PARAM_RANGE_STEPS_DEFAULT

        self.source = WeatherGovSource(location, rangeDict)


    def __repr__(self):
        try:
            source = self.source
        except AttributeError:
            source = '<no source>'
        return '{cls}({source})'.format(cls=self.__class__.__name__, source=source)


    @property
    def location(self):
        return self.source.location


    # ==== calendar layout methods ====

    def calendarHeaderRow(self):
        dayOfWeekNames = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        oldestHour = self.source.hours[0]
        newestHour = self.source.hours[-1]
        numDays = 1 + (newestHour.datetime - oldestHour.datetime).days
        weekday = oldestHour.datetime.weekday()
        headerRow = (dayOfWeekNames * 3)[
                    weekday:weekday + numDays]  # 3 is magic. at least good enough for 8 days of forecast data
        return headerRow


    @staticmethod
    def rowHeadingForHour(hourOfDay):
        """
        :param hourOfDay: 0 through 23. indexes into hoursAsCalendarRows()
        :return: AM/PM version of hour
        """
        if hourOfDay < 13:
            return '{}'.format(hourOfDay)
        else:
            return '{}p'.format(hourOfDay - 12)


    def hoursAsCalendarRows(self):
        """
        Helper method used by views to lay out my hours in a calendar-like view.
        
        :return: Format: a list of 24 8-tuples containing day-of-the-week Hours. Conceptually returns a table where 
        there are 24 rows correspond to hours of the day (0 through 23), and 8 columns corresponding to the days of 
        the week. Each cell is the Hour for that combination of hourOfDay and dayOfWeek. (Note that we have 8
        columns and not 7 because a 7-day forecast will very likely 'overflow' into an eighth day. Not having 7 is OK 
        because the display is not a weekly calendar; it's a tabular display that's extended into the future as far 
        necessary. If 14 day forecasts become available then we will have 15 columns, and so forth.) To get a table 
        with no missing Hours, we have to interpolate from the most recently seen Hour, similar to what 
        hoursWithGapsFromXml() does.
        """
        # since we have my hours, which have no gaps, we need to: 1) create missing Hours from hour 0 of the
        # first day to the first sampled hour - call those the head missing hours, and 2) create missing Hours from the
        # last sampled hour to hour 23 of that last day - call those the tail missing hours
        from forecast.Hour import Hour
        oneHour = datetime.timedelta(hours=1)

        # create headMissingHours by working backward from the closest hour until the date goes to the previous day
        closestHour = self.source.hours[0]
        headMissingHours = []
        closestDay = closestHour.datetime.day
        currDatetime = closestHour.datetime - oneHour
        while currDatetime.day == closestDay:
            headMissingHours.append(Hour(currDatetime))
            currDatetime -= oneHour
        headMissingHours.sort()

        # create tailMissingHours by working forward from the farthest hour until the date goes to the next day
        tailMissingHours = []
        farthestHour = self.source.hours[-1]
        farthestDay = farthestHour.datetime.day
        currDatetime = farthestHour.datetime + oneHour
        while currDatetime.day == farthestDay:
            tailMissingHours.append(Hour(currDatetime))
            currDatetime += oneHour
        tailMissingHours.sort()

        # rows
        allHours = headMissingHours + self.source.hours + tailMissingHours
        numDays = 1 + (farthestHour.datetime - closestHour.datetime).days
        calendarRows = []
        for hourNum in range(24):  # calendar row
            hourRow = []
            for dayNum in range(numDays):  # calendar column
                hour = allHours[hourNum + (24 * dayNum)]
                hourRow.append(hour)
            calendarRows.append(hourRow)
        return calendarRows


