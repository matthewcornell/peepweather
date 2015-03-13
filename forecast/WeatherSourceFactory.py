from forecast.WeatherGovSource import WeatherGovSource


class WeatherSourceFactory(object):
    """
    """


    @staticmethod
    def makeSource(sourceName, location, forecast):
        """
        :param sourceName: one of the following: currently only 'weather.gov'
        :param location: Location to use for the source's forecast
        :param forecast: Forecast instance to pass through for Hours
        :return: a WeatherSource instance for sourceName
        """
        if sourceName == 'weather.gov':
            return WeatherGovSource(location, forecast)
        else:
            raise ValueError("sourceName did not name a valid WeatherSource factory: ".format(sourceName))
