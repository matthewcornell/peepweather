from forecast.Location import Location


class WeatherSource(object):
    """
    Abstract class that represents an online weather source that provides forecast information for a particular
    Location. Stored as a sequence of Hour instances. These have no gaps, i.e., there is one Hour for every hour,
    and all time zone information is normalized. (weather.gov mixes time zones, and has gaps in forecasts.)
    """


    def __init__(self, location, forecast):
        """
        :param location: a Location
        :param forecast: a Forecast. passed through to Hour instantiation
        """
        if not isinstance(location, Location):
            raise ValueError("location is not a Location instance: {}".format(location))

        from forecast.Forecast import Forecast  # smelly avoidance of recursive import

        if not isinstance(forecast, Forecast):
            raise ValueError("forecast is not a Forecast instance: {}".format(forecast))

        self.hours = self.makeHours(location, forecast)
        self.location = location


    def __repr__(self):
        return '{cls}({location})'.format(
            cls=self.__class__.__name__, location=self.location.__repr__())


    def makeHours(self, location, forecast):
        """
        :return: a list of Hour instances for location
        """
        raise NotImplementedError()
