class Hour():
    def __init__(self, datetime, precip=None, temp=None, wind=None):
        self.datetime = datetime
        self.precip = precip
        self.temp = temp
        self.wind = wind


    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, repr(self.datetime),
                                           self.precip, self.temp, self.wind)


    def key(self):
        return self.datetime, self.precip, self.temp, self.wind


    def __eq__(self, other):
        return type(self) == type(other) and self.key() == other.key()


    def __hash__(self):
        return hash(self.key())
