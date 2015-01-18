from functools import total_ordering


@total_ordering
class Hour():
    P_DES_LOW, P_DES_MED, P_DES_HIGH = range(0, 3)  # desirability rating for the three individual parameters
    H_DES_LOW, H_DES_MED_LOW, H_DES_MED_HIGH, H_DES_HIGH = range(0, 4)  # overall desirability rating for an hour, based on above parameter desirabilities
    
    # from this scheme: http://colorbrewer2.org/?type=sequential&scheme=OrRd&n=4
    HOUR_DESIRABILITY_TO_COLOR = {H_DES_LOW: 'low',
                                  H_DES_MED_LOW: 'med low',
                                  H_DES_MED_HIGH: 'med high',
                                  H_DES_HIGH: 'high'}
    # HOUR_DESIRABILITY_TO_COLOR = {H_DES_LOW: '#fef0d9',
    #                               H_DES_MED_LOW: '#fdcc8a',
    #                               H_DES_MED_HIGH: '#fc8d59',
    #                               H_DES_HIGH: '#d7301f'}


    def __init__(self, datetime, precip=None, temp=None, wind=None):
        """
        pass None for the weather parameters to represent missing data, i.e., a 'missing' hour
        :param datetime: 
        :param precip: 
        :param temp: 
        :param wind: 
        :return:
        """
        self.datetime = datetime  # time of forecast. always on the hour, i.e., only the day and hour matter. minutes, etc. are ignored
        self.precip = precip  # probability of precipitation percent: integers range(101). TODO couldn't find docs about range end
        self.temp = temp  # degrees Fahrenheit: integers (negative and possitive)
        self.wind = wind  # MPH: whole numbers (integers from 0 up)


    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, repr(self.datetime),
                                           self.precip, self.temp, self.wind)


    def __str__(self):
        return '{} | {}°F, {} MPH, {}%'.format(
            self.datetime.strftime('%a %m/%d %H:%M') if self.datetime else "time?", self.temp, self.wind, self.precip)


    def key(self):
        return self.datetime, self.precip, self.temp, self.wind


    def __eq__(self, other):
        return type(self) == type(other) and self.key() == other.key()


    def __hash__(self):
        return hash(self.key())


    def __lt__(self, other):
        return self.datetime < other.datetime


    #
    # color-related methods
    #

    def color(self):
        """
        :return: an HTML color string based on my weather settings
        """
        hDesHighCount = Hour.paramDesirabilityForValue('precip', self.precip)
        hDesMedCount = Hour.paramDesirabilityForValue('temp', self.temp)
        hDesLowCount = Hour.paramDesirabilityForValue('wind', self.wind)
        hourDesirability = self.hourDesirabilityForParamDesCounts(hDesLowCount, hDesMedCount, hDesHighCount)
        color = self.colorForHourDesirability(hourDesirability)
        print('xx color', (hDesHighCount, hDesMedCount, hDesLowCount), hourDesirability, color)
        return color


    @classmethod
    def colorForHourDesirability(cls, hourDesirability):
        """
        Returns a color corresponding to hourDesirability, which comes from (hourDesirabilityForParamDesCounts)
        :param hourDesirability:
        :return: an HTML color
        """
        color = Hour.HOUR_DESIRABILITY_TO_COLOR[hourDesirability]
        print('yy colorForHourDesirability', hourDesirability, color)
        return color


    @classmethod
    def hourDesirabilityForParamDesCounts(cls, hDesLowCount, hDesMedCount, hDesHighCount):
        """
        Gives an overall rating for a set of paramaneter desirability counts.
        
        :param paramDesireTuple: a 3-tuple of counts for these param desirabilities, in order:
            (Hour.P_DES_LOW, Hour.P_DES_MED, Hour.P_DES_HIGH)
        :return: one of H_DES_LOW, H_DES_MED_LOW, H_DES_MED_HIGH, H_DES_HIGH
        """
        if hDesLowCount:  # if any are low then overall is low
            return Hour.H_DES_LOW
        elif hDesHighCount == 3:  # if all three are high then overall is high
            return Hour.H_DES_HIGH
        elif hDesMedCount == 1 and hDesHighCount == 2:  # if there are two highs then overall is med-high
            return Hour.H_DES_MED_HIGH
        elif hDesMedCount == 2 and hDesHighCount == 1:  # if there are two mediums then overall is med-low
            return Hour.H_DES_MED_LOW
        else:
            raise ValueError("invalid counts: {}, {}, {}".format(hDesLowCount, hDesMedCount, hDesHighCount))


    @classmethod
    def paramDesirabilityForValue(cls, paramName, value):
        """
        Gives a rating for a particular parameter value.
        
        :param paramName: one of ['precip', 'temp', 'wind']
        :param value: the parameter's value
        :return: one of P_DES_LOW, P_DES_MED, P_DES_HIGH based on the passed parameter . for now uses the following ranges to decide:

            precip: [0, 10]: Hour.P_DES_HIGH    [11, 30]: Hour.P_DES_MED    [31, ...]: Hour.P_DES_LOW
            temp: [..., 32]: Hour.P_DES_LOW    [33, 41]: Hour.P_DES_MED    [42, 70] Hour.P_DES_HIGH    [71, 85]: Hour.P_DES_MED    [86, ...]: Hour.P_DES_LOW
            wind:   [0,  8]: Hour.P_DES_HIGH    [ 9, 12]: Hour.P_DES_MED    [13, ...]: Hour.P_DES_LOW
        """
        if paramName not in ['precip', 'temp', 'wind']:
            raise ValueError("invalid parameter: {}".format(paramName))

        if paramName == 'precip':
            if value <= 10:
                return Hour.P_DES_HIGH
            elif value >= 31:
                return Hour.P_DES_LOW
            else:
                return Hour.P_DES_MED
        # temp
        elif paramName == 'temp':
            if value <= 32 or value >= 86:
                return Hour.P_DES_LOW
            elif 33 <= value <= 41 or 71 <= value <= 85:
                return Hour.P_DES_MED
            else:
                return Hour.P_DES_HIGH
        # wind
        else:
            if value <= 8:
                return Hour.P_DES_HIGH
            elif value >= 13:
                return Hour.P_DES_LOW
            else:
                return Hour.P_DES_MED
