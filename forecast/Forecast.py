import datetime
import logging

from forecast.Hour import Hour

from forecast.Location import Location
from forecast.WeatherSourceFactory import WeatherSourceFactory


logger = logging.getLogger(__name__)


class Forecast:
    """
    Computes a forecast based on a zip code using http://www.nws.noaa.gov/ndfd/technical.htm as a sequence of Hours.
    """

    # default ranges (AKA a 'range dict'). see range-documentation.txt for detail
    PARAM_RANGE_STEPS_DEFAULT = {'precip': [10, 30],  # H->M, M->L
                                 'temp': [35, 59, 89, 100],  # L->, M->H, H->, M->L
                                 'wind': [8, 12],  # H->M, M->L
                                 'clouds': [33, 66],  # H->M, M->L
    }


    def __init__(self, location, sourceName, rangeDict=None, weatherSourceFactory=WeatherSourceFactory):
        """
        :param location: location to get the forecast for
        :param rangeDict: optional as in PARAM_RANGE_STEPS_DEFAULT. uses that default if not passed
        :param elementTree: optional ElementTree to use for testing to bypass urlopen() call
        :return:
        """
        # check location
        if not isinstance(location, Location):
            raise ValueError("location is not a Location instance: {}".format(location))

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

        # instantiate the WeatherSource
        self.source = weatherSourceFactory.makeSource(sourceName, location, self)


    def __repr__(self):
        return '{cls}({source})'.format(cls=self.__class__.__name__, source=self.source)


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
        oneHour = datetime.timedelta(hours=1)

        # normalize my Hours' timezones b/c weather service sometimes changes tz *within* one <time-layout> - go figure
        # - and this causes problems: see testHoursAsCalendarRowsIndexOutOfBounds(). we normalize by:
        # 1) adopting the first/closest Hour's TZ as the standard for the calendar, and
        # 2) work forward through ea. Hour, adding one hour and saving that as a new Hour's new datetime
        #
        closestHour = self.source.hours[0]
        normalizedHours = [closestHour]
        for index, hour in enumerate(self.source.hours[1:]):
            newHour = Hour(closestHour.datetime + (oneHour * (index + 1)),
                           hour.rangeDict, hour.precip, hour.temp, hour.wind, hour.clouds)
            normalizedHours.append(newHour)

        # create headMissingHours by working backward from the closest hour until the date goes to the previous day
        headMissingHours = []
        closestDay = closestHour.datetime.day
        currDatetime = closestHour.datetime - oneHour
        while currDatetime.day == closestDay:
            headMissingHours.append(Hour(currDatetime, self.rangeDict))
            currDatetime -= oneHour
        headMissingHours.sort()

        # create tailMissingHours by working forward from the farthest hour until the date goes to the next day
        tailMissingHours = []
        farthestHour = normalizedHours[-1]
        farthestDay = farthestHour.datetime.day
        currDatetime = farthestHour.datetime + oneHour
        while currDatetime.day == farthestDay:
            tailMissingHours.append(Hour(currDatetime, self.rangeDict))
            currDatetime += oneHour
        tailMissingHours.sort()

        # rows
        allHours = headMissingHours + normalizedHours + tailMissingHours
        numDays = 1 + (farthestHour.datetime - closestHour.datetime).days
        calendarRows = []
        for hourNum in range(24):  # calendar row
            hourRow = []
            for dayNum in range(numDays):  # calendar column
                hour = allHours[hourNum + (24 * dayNum)]
                hourRow.append(hour)
            calendarRows.append(hourRow)
        return calendarRows


