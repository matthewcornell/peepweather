import datetime
import unittest

from forecast.WeatherSource import WeatherSource
from forecast.Forecast import Forecast

from forecast.Hour import Hour
from forecast.Location import Location


class TestSource(WeatherSource):
    HOURS = [Hour(datetime.datetime(2015, 1, 13, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                  Forecast.PARAM_RANGE_STEPS_DEFAULT, None, None, None),
             Hour(datetime.datetime(2015, 1, 14, 1, 0, tzinfo=datetime.timezone(datetime.timedelta(-1, 68400))),
                  Forecast.PARAM_RANGE_STEPS_DEFAULT, 0, 3, 2, -1)]


    def makeHours(self):
        return self.HOURS


class ForecastTestCase(unittest.TestCase):
    def testForecastConstructor(self):
        location = Location('42.375370', '-72.519249')
        forecast = Forecast(location, TestSource)
        self.assertTrue(isinstance(forecast.source, TestSource))
        self.assertEqual(location, forecast.source.location)

        rangeDict = Forecast.PARAM_RANGE_STEPS_DEFAULT
        forecast = Forecast(location, TestSource, rangeDict)
        self.assertEqual(rangeDict, forecast.rangeDict)

        with self.assertRaisesRegex(ValueError, "location is not a Location instance: None"):
            Forecast(None, TestSource, rangeDict)

        with self.assertRaisesRegex(ValueError, "sourceClass is not a WeatherSource subclass: None"):
            Forecast(location, None, rangeDict)

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
                Forecast(location, TestSource, rangeDict)


    def testForecastHours(self):
        location = Location('42.375370', '-72.519249')
        forecast = Forecast(location, TestSource)
        for expHour, actHour in zip(TestSource.HOURS, forecast.hours):
            self.assertEqual(expHour, actHour)


    def testFillsGaps_TODO(self):
        self.fail()  # todo


    def testUSGovWeatherSourceSanityCheck_TODO(self):
        self.fail()  # todo


    def testHourDaylight_TODO(self):
        self.fail()  # todo move from Forecast to Hour
