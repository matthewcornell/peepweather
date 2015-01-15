class Hour():
    def __init__(self, datetime, precip=None, temp=None, wind=None):
        self.datetime = datetime
        self.precip = precip
        self.temp = temp
        self.wind = wind

    def __repr__(self):
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, self.datetime, self.precip, self.temp, self.wind)
