from forecast.Location import Location


class WeatherSource(object):
    """
    Abstract class that represents an online weather source that provides forecast information for a particular
    Location. Stored as a sequence of Hour instances. Note that depending on the source, the Hours might have gaps,
    i.e., they might not be instances for every hour. We leave it to Forecast to fill in the gaps once it instantiates
    a WeatherSource.
    """


    def __init__(self, location):
        if not isinstance(location, Location):
            raise ValueError("location is not a Location instance: {}".format(location))
        
        self.location = location
        
        
    def __repr__(self):
        return '{cls}({location})'.format(
            cls=self.__class__.__name__, location=self.location.__repr__())


    def makeHours(self):
        """
        :return: a list of Hour instances, possibly with gaps
        """
        raise NotImplementedError()

