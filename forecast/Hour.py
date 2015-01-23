from functools import total_ordering
from numbers import Number


@total_ordering
class Hour():
    # desirability rating for the three individual parameters
    P_DES_LOW, P_DES_MED, P_DES_HIGH = ['P_DES_LOW', 'P_DES_MED', 'P_DES_HIGH']

    # overall desirability rating for an hour, based on above parameter desirabilities:
    H_DES_LOW, H_DES_MED_LOW, H_DES_MED_HIGH, H_DES_HIGH = 'H_DES_LOW', 'H_DES_MED_LOW', 'H_DES_MED_HIGH', 'H_DES_HIGH'

    # color definitions based on the HSV gradient b/w red and green: http://www.colorhexa.com/ff0000-to-00ff00
    HOUR_DESIRABILITY_TO_COLOR = {H_DES_LOW: '#ff0000',
                                  H_DES_MED_LOW: '#ffaa00',
                                  H_DES_MED_HIGH: 'd5ff00',
                                  H_DES_HIGH: '00ff00'}

    HOUR_MISSING_COLOR = 'white'
    
    COLOR_SEQ_HIGH_TO_LOW = [HOUR_DESIRABILITY_TO_COLOR[H_DES_HIGH],
                             HOUR_DESIRABILITY_TO_COLOR[H_DES_MED_HIGH],
                             HOUR_DESIRABILITY_TO_COLOR[H_DES_MED_LOW],
                             HOUR_DESIRABILITY_TO_COLOR[H_DES_LOW]]  # for views
    
    # default ranges (see range-documentation.txt)
    PARAM_RANGE_STEPS = {'precip': [10, 30],  # H-M-L
                         'wind': [8, 12],     # H-M-L
                         'temp': [32, 41, 70, 85]}  # L-M-H-M-L


    def __init__(self, datetime, precip=None, temp=None, wind=None):
        """
        Pass None for the weather parameters to represent missing data, i.e., a 'missing' hour.
        """
        self.datetime = datetime  # time of forecast. always on the hour, i.e., only the day and hour matter. minutes, etc. are ignored
        self.precip = precip  # probability of precipitation percent: integers range(101). TODO couldn't find docs about range end
        self.temp = temp  # degrees Fahrenheit: integers (negative and possitive)
        self.wind = wind  # MPH: whole numbers (integers from 0 up)


    def key(self):
        return self.datetime, self.precip, self.temp, self.wind


    def __eq__(self, other):
        return type(self) == type(other) and self.key() == other.key()


    def __hash__(self):
        return hash(self.key())


    def __lt__(self, other):
        return self.datetime < other.datetime


    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, repr(self.datetime),
                                           self.precip, self.temp, self.wind)


    def __str__(self):
        if self.precip is None:
            return '{} | no data'.format(self.datetime.strftime('%a %m/%d %H:%M'))
        else:
            return '{} | {}%, {}°F, {} MPH'.format(
                self.datetime.strftime('%a %m/%d %H:%M') if self.datetime else "time?", self.precip, self.temp,
                self.wind)


    def detailString(self):
        if self.precip is None:
            return str(self)
        else:
            desirabilityToChar = {Hour.P_DES_HIGH: 'H', Hour.P_DES_MED: 'M', Hour.P_DES_LOW: 'L', }
            return '{} | {}% ({}), {}°F ({}), {} MPH ({})'.format(
                self.datetime.strftime('%a %m/%d %H:%M') if self.datetime else "time?",
                self.precip, desirabilityToChar[Hour.paramDesirabilityForValue('precip', self.precip)],
                self.temp, desirabilityToChar[Hour.paramDesirabilityForValue('temp', self.temp)],
                self.wind, desirabilityToChar[Hour.paramDesirabilityForValue('wind', self.wind)])


    #
    # color-related methods
    #

    def color(self):
        """
        :return: an HTML color string based on my weather settings
        """
        if self.precip is None:
            return Hour.HOUR_MISSING_COLOR

        hDesHighCount = 0
        hDesMedCount = 0
        hDesLowCount = 0
        paramDesirabilities = [Hour.paramDesirabilityForValue('precip', self.precip),
                               Hour.paramDesirabilityForValue('temp', self.temp),
                               Hour.paramDesirabilityForValue('wind', self.wind)]
        for paramDesirability in paramDesirabilities:
            if paramDesirability == Hour.P_DES_LOW:
                hDesLowCount += 1
            elif paramDesirability == Hour.P_DES_MED:
                hDesMedCount += 1
            else:
                hDesHighCount += 1
        hourDesirability = self.hourDesirabilityForParamDesCounts(hDesLowCount, hDesMedCount, hDesHighCount)
        color = self.colorForHourDesirability(hourDesirability)
        return color


    @classmethod
    def colorForHourDesirability(cls, hourDesirability):
        """
        Returns a color corresponding to hourDesirability, which comes from (hourDesirabilityForParamDesCounts)
        :param hourDesirability:
        :return: an HTML color
        """
        return Hour.HOUR_DESIRABILITY_TO_COLOR[hourDesirability]


    @classmethod
    def hourDesirabilityForParamDesCounts(cls, hDesLowCount, hDesMedCount, hDesHighCount):
        """
        Gives an overall rating for a set of paramaneter desirability counts.

        :param paramDesireTuple: a 3-tuple of counts for these param desirabilities, in order:
            (Hour.P_DES_LOW, Hour.P_DES_MED, Hour.P_DES_HIGH)
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


    @classmethod
    def paramDesirabilityForValue(cls, paramName, value):
        """
        Gives a rating for a particular parameter value using the current ranges.

        :param paramName: one of ['precip', 'temp', 'wind']
        :param value: the parameter's value
        :return: one of P_DES_LOW, P_DES_MED, P_DES_HIGH based on the passed parameter
        """
        if paramName not in Hour.PARAM_RANGE_STEPS.keys():
            raise ValueError("invalid parameter: {}".format(paramName))

        paramStep = Hour.PARAM_RANGE_STEPS[paramName]
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
