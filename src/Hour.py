class Hour():
    def __init__(self, datetime, precip=None, temp=None, wind=None):
        self.datetime = datetime    # from datetime import datetime. time of forecast. always on the hour, i.e., only the day and hour matter. minutes, etc. are ignored
        self.precip = precip        # probability of precipitation: % b/w 0 and 100
        self.temp = temp            # degrees Fahrenheit
        self.wind = wind            # MPH


    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, repr(self.datetime),
                                           self.precip, self.temp, self.wind)


    def key(self):
        return self.datetime, self.precip, self.temp, self.wind


    def __eq__(self, other):
        return type(self) == type(other) and self.key() == other.key()


    def __hash__(self):
        return hash(self.key())
