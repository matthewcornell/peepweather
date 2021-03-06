import ephem
from numbers import Number

from functools import total_ordering


@total_ordering
class Hour():
    # desirability rating for the three individual parameters
    P_DES_LOW, P_DES_MED, P_DES_HIGH = ['P_DES_LOW', 'P_DES_MED', 'P_DES_HIGH']

    # overall desirability rating for an hour, based on above parameter desirabilities:
    H_DES_LOW, H_DES_MED_LOW, H_DES_MED_HIGH, H_DES_HIGH = 'H_DES_LOW', 'H_DES_MED_LOW', 'H_DES_MED_HIGH', 'H_DES_HIGH'


    def __init__(self, datetime, precip=None, temp=None, wind=None, clouds=None):
        """
        Pass None for the weather parameters to represent missing data, i.e., a 'missing' hour.
        """
        self.datetime = datetime  # time of forecast. always on the hour, i.e., only the day and hour matter. minutes, etc. are ignored
        self.precip = precip  # probability of precipitation percent: integers range(101). todo couldn't find docs about range end
        self.temp = temp  # degrees Fahrenheit: integers (negative and possitive)
        self.wind = wind  # MPH: whole numbers (integers from 0 up)
        self.clouds = clouds  # cloud cover percentage


    def key(self):
        return self.datetime, self.precip, self.temp, self.wind


    def __eq__(self, other):
        return type(self) == type(other) and self.key() == other.key()


    def __hash__(self):
        return hash(self.key())


    def __lt__(self, other):
        return self.datetime < other.datetime


    def __repr__(self):
        return '{}({}, {}, {}, {}, {})'.format(self.__class__.__name__, repr(self.datetime),
                                               self.precip, self.temp, self.wind, self.clouds)


    def __str__(self):
        if self.isMissingHour():
            return '{} | no data'.format(self.datetime.strftime('%a %m/%d %H:%M'))
        else:
            return '{} | {}%, {}°F, {} MPH, {}%'.format(
                self.datetime.strftime('%a %m/%d %H:%M') if self.datetime else "time?", self.precip, self.temp,
                self.wind, self.clouds)


    def isMissingHour(self):
        return self.precip is None or self.temp is None or self.wind is None or self.clouds is None


    # ==== daylight methods ====

    def isDaylight(self, forecast):
        """
        :param forecast provides the lat/lon to location this Hour at
        :return: main method that returns True if I am in daylight hours according to isDaylightDatetime()
        """
        return Hour.isDaylightDatetime(forecast.source.location, self.datetime)


    @classmethod
    def isDaylightDatetime(cls, location, dt):
        """
        internal method
        :param latLon: 2-tuple of strings
        :param dt: a Python datetime containing timezone information as returned by Forecast.parseStartValidTime()
        :return: True if dt is daytime according to my latLon, and False o/w
        """
        if not dt.tzinfo:
            raise ValueError("datetime has no tzinfo: {!r}".format(dt))  # 'naive' datetime

        observer = ephem.Observer()
        observer.lat = location.latitude
        observer.lon = location.longitude

        # now set observer.date. Note: because forecast times are local to the lat/lon (<time-layout time-coordinate="local" ...">),
        # and because ephem requires all dates in UTC and does not honor time zones, we need to covert to UTC. do so by
        # adding the # hours represented by the included datetime timezone
        tzd = dt.tzinfo.utcoffset(None)
        e = ephem.Date(dt)
        tzUtcOffsetHours = (tzd.days * 24) + (tzd.seconds / (60 * 60))
        eMinusTzdHours = e - (tzUtcOffsetHours * ephem.hour)  # 42017.25 Q: intuition behind subtracting?
        observer.date = ephem.Date(eMinusTzdHours)

        sun = ephem.Sun()
        sun.compute(observer)
        twilight = -12 * ephem.degree
        isDaylight = sun.alt > twilight
        return isDaylight


    # ==== UI methods ====

    def detailString(self, rangeDict):
        """

        :param rangeDict:
        :return: 2-tuple of strings for popover display: (title, body)
        """
        dateTimeStr = '{}'.format(self.datetime.strftime('%a %m/%d %I:%M %p'))
        if self.isMissingHour():
            return dateTimeStr, "No data"
        else:
            titleStr = '{} - {}'.format(dateTimeStr, self.cssClassForDesirability(rangeDict))
            paramDesToChar = {Hour.P_DES_HIGH: '&check;', Hour.P_DES_MED: '~', Hour.P_DES_LOW: 'x', }
            bodyStr = '{}&nbsp;<strong>Precip</strong>:&nbsp;{}%, {}&nbsp;<strong>Temp</strong>:&nbsp;{}°F, ' \
                      '{}&nbsp;<strong>Wind</strong>:&nbsp;{}&nbsp;MPH, {}&nbsp;<strong>Clouds</strong>:&nbsp;{}%'.format(
                paramDesToChar[
                    self.paramDesirabilityForValue('precip', self.precip, rangeDict)], self.precip,
                paramDesToChar[self.paramDesirabilityForValue('temp', self.temp, rangeDict)], self.temp,
                paramDesToChar[self.paramDesirabilityForValue('wind', self.wind, rangeDict)], self.wind,
                paramDesToChar[
                    self.paramDesirabilityForValue('clouds', self.clouds, rangeDict)], self.clouds)
            return titleStr, bodyStr


    def cssClassForDesirability(self, rangeDict):
        """

        :param rangeDict:
        :return: a css class from /static/hour-colors.css, factoring in my clouds
        """
        if self.isMissingHour():
            return 'Missing'

        hourDesirabilityToClass = {Hour.H_DES_LOW: 'Poor',
                                   Hour.H_DES_MED_LOW: 'Fair',
                                   Hour.H_DES_MED_HIGH: 'Okay',
                                   Hour.H_DES_HIGH: 'Great'}
        return hourDesirabilityToClass[self.desirability(rangeDict)]


    def charIconsForParams(self, rangeDict):
        """

        :param rangeDict:
        :return: list of three Weather Icons 'specific icon class' strings, one each for precip, temp, and wind
        respectively, or None if no applicable. 
        """
        chars = [None, None, None]  # precip, temp, wind

        if self.isMissingHour():
            return chars

        # add precip or clouds
        precipDes = self.paramDesirabilityForValue('precip', self.precip, rangeDict)
        cloudsDes = self.paramDesirabilityForValue('clouds', self.clouds, rangeDict)
        if precipDes == Hour.P_DES_LOW:
            chars[0] = 'wi-rain'
        elif precipDes == Hour.P_DES_MED:
            chars[0] = 'wi-showers'
        elif cloudsDes == Hour.P_DES_LOW:  # add a cloud icon if it's cloudy and no other cloud-containing icons are present due to precip
            chars[0] = 'wi-cloudy'  # double clouds
        elif cloudsDes == Hour.P_DES_MED:
            chars[0] = 'wi-cloud'  # single cloud

        # add temp
        tempDes = self.paramDesirabilityForValue('temp', self.temp, rangeDict)
        if tempDes == Hour.P_DES_LOW:
            chars[1] = 'wi-thermometer'
        elif tempDes == Hour.P_DES_MED:
            chars[1] = 'wi-thermometer-exterior'

        # add wind
        windDes = self.paramDesirabilityForValue('wind', self.wind, rangeDict)
        if windDes == Hour.P_DES_LOW:
            chars[2] = 'wi-strong-wind'
        elif windDes == Hour.P_DES_MED:
            chars[2] = 'wi-windy'

        return chars


    # ==== analysis methods ====

    def desirability(self, rangeDict):
        """

        :param rangeDict:
        :return: overall desirability based on my parameters. one of H_DES_LOW, H_DES_MED_LOW, H_DES_MED_HIGH, H_DES_HIGH
        returns None if this is a missing hour. NB: Does not factor in cloudiness.
        """
        if self.isMissingHour():
            return None

        hDesHighCount = 0
        hDesMedCount = 0
        hDesLowCount = 0
        paramDesirabilities = [
            self.paramDesirabilityForValue('precip', self.precip, rangeDict),
            self.paramDesirabilityForValue('temp', self.temp, rangeDict),
            self.paramDesirabilityForValue('wind', self.wind, rangeDict)]
        for paramDesirability in paramDesirabilities:
            if paramDesirability == Hour.P_DES_LOW:
                hDesLowCount += 1
            elif paramDesirability == Hour.P_DES_MED:
                hDesMedCount += 1
            else:
                hDesHighCount += 1
        return self.hourDesirabilityForParamDesCounts(hDesLowCount, hDesMedCount, hDesHighCount)


    @classmethod
    def hourDesirabilityForParamDesCounts(cls, hDesLowCount, hDesMedCount, hDesHighCount):
        """
        Gives an overall rating for a set of parameter desirability counts.

        :param hDesLowCount, hDesMedCount, hDesHighCount: counts for these param desirabilities, in order:
            Hour.P_DES_LOW, Hour.P_DES_MED, Hour.P_DES_HIGH. NB: Should only include precip, temp, and wind, and
            *not* clouds
        :return: one of H_DES_LOW, H_DES_MED_LOW, H_DES_MED_HIGH, H_DES_HIGH
        """
        if not all(map(lambda count: isinstance(count, Number), (hDesLowCount, hDesMedCount, hDesHighCount))):
            raise ValueError("counts weren't all numbers: {}".format((hDesLowCount, hDesMedCount, hDesHighCount)))

        if hDesLowCount + hDesMedCount + hDesHighCount != 3:
            raise ValueError("counts didn't add to 3: {}".format((hDesLowCount, hDesMedCount, hDesHighCount)))

        if hDesLowCount:  # if any are low then overall is low
            return Hour.H_DES_LOW
        elif hDesHighCount == 3:  # if all three are high then overall is high
            return Hour.H_DES_HIGH
        elif hDesMedCount == 1 and hDesHighCount == 2:  # if there are two highs then overall is med-high
            return Hour.H_DES_MED_HIGH
        # elif hDesMedCount == 2 and hDesHighCount == 1:  # if there are two mediums then overall is med-low
        else:
            return Hour.H_DES_MED_LOW


    def paramDesirabilityForValue(self, paramName, value, rangeDict):
        """
        Gives a rating for a particular parameter value using the current ranges.

        :param rangeDict:
        :param paramName: one of ['precip', 'temp', 'wind', 'clouds']
        :param value: the parameter's value
        :return: one of P_DES_LOW, P_DES_MED, P_DES_HIGH based on the passed parameter
        """
        if paramName not in rangeDict.keys():
            raise ValueError("invalid parameter: {}".format(paramName))

        paramStep = rangeDict[paramName]
        if len(paramStep) == 2:  # H-M-L
            if value < paramStep[0]:
                return Hour.P_DES_HIGH
            elif value >= paramStep[1]:
                return Hour.P_DES_LOW
            else:
                return Hour.P_DES_MED
        else:  # L-M-H-M-L
            if value < paramStep[0] or value >= paramStep[3]:
                return Hour.P_DES_LOW
            elif paramStep[1] <= value < paramStep[2]:
                return Hour.P_DES_HIGH
            else:
                return Hour.P_DES_MED
