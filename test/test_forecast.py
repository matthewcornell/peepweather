import unittest
import datetime

from mock import Mock, patch

from forecast.Forecast import Forecast
from forecast.Location import Location


class ForecastTestCase(unittest.TestCase):
    """
    """

    def testCalendarHeaderRow_TODO(self):
        self.fail()


    def testRowHeadingForHour_TODO(self):
        self.fail()


    def testHoursAsCalendarRows_TODO(self):
        self.fail()


    @patch('forecast.Forecast.WeatherGovSource')
    def testForecastRangeDict(self, MockWeatherGovSource):
        location = Location('42.375370', '-72.519249')
        rangeDict = Forecast.PARAM_RANGE_STEPS_DEFAULT
        forecast = Forecast(location)
        self.assertEqual(rangeDict, forecast.rangeDict)

        for rangeDict, errorMessage in [
            (1, "rangeDict is not a dict"),
            ({'precip': None, 'temp': None, 'clouds': None}, "rangeDict is missing a parameter key"),
            ({'precip': None, 'temp': None, 'wind': None, 'clouds': None}, "rangeDict values were not all lists"),
            ({'precip': [], 'temp': [], 'wind': [], 'clouds': []}, "rangeDict values were not all lists of ints"),
            ({'precip': [1, 2, 3], 'temp': [4, 5, 6, 7], 'wind': [8, 9], 'clouds': [10, 11]},
             "rangeDict precip, wind, or clouds is not a list of two ints"),
            ({'precip': [1, 2], 'temp': [4, 5, 6], 'wind': [8, 9], 'clouds': [10, 11]},
             "rangeDict temp is not a list of four ints"),
            ({'precip': [1, 2], 'temp': [4, 5, 6, 7], 'wind': [8], 'clouds': [10, 11]},
             "rangeDict precip, wind, or clouds is not a list of two ints"),
            ({'precip': [1, 2], 'temp': [4, 5, 6, 7], 'wind': [8, 9], 'clouds': [10]},
             "rangeDict precip, wind, or clouds is not a list of two ints"),
            ({'precip': [2, 1], 'temp': [4, 5, 6, 7], 'wind': [8, 9], 'clouds': [10, 11]},
             "rangeDict values were not all sorted"),
            ({'precip': [1, 2], 'temp': [4, 5, 7, 6], 'wind': [8, 9], 'clouds': [10, 11]},
             "rangeDict values were not all sorted"),
        ]:
            with self.assertRaisesRegex(ValueError, errorMessage):
                Forecast(location, rangeDict=rangeDict)


    def testForecastSource(self):
        with self.assertRaisesRegex(ValueError, "location is not a Location instance"):
            Forecast(None)

        location = Location('42.375370', '-72.519249')
        with patch ('forecast.Forecast.WeatherGovSource') as MockWeatherGovSource:
            MockWeatherGovSource.side_effect = ValueError("error message")
            with self.assertRaisesRegex(ValueError, "error message"):
                Forecast(location)

        with patch ('forecast.Forecast.WeatherGovSource') as MockWeatherGovSource:
            fakeInstance = 'fake instance'
            MockWeatherGovSource.return_value = fakeInstance
            forecast = Forecast(location)
            self.assertEqual(fakeInstance, forecast.source)
