import xml.etree.ElementTree as ET
import unittest
from unittest.mock import patch

from forecast.WeatherGovSource import WeatherGovSource

from forecast.Sticker import Sticker
from forecast.Location import Location
from forecast.Forecast import Forecast


class ForecastTestCase(unittest.TestCase):
    """
    """


    @patch('forecast.Forecast.WeatherGovSource')
    def testForecastRangeDict(self, MockWeatherGovSource):
        from forecast.Forecast import Forecast  # avoid circular imports

        location = Location('01002')
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

        location = Location('01002')
        with patch('forecast.Forecast.WeatherGovSource') as MockWeatherGovSource:
            MockWeatherGovSource.side_effect = ValueError("error message")
            with self.assertRaisesRegex(ValueError, "error message"):
                Forecast(location)

        with patch('forecast.Forecast.WeatherGovSource') as MockWeatherGovSource:
            MockWeatherGovSource.return_value = 'fake instance'
            forecast = Forecast(location)
            self.assertEqual('fake instance', forecast.source)


    @patch('forecast.Forecast.WeatherGovSource')
    def testSticker(self, MockWeatherGovSource):
        # sanity-check that Sticker() doesn't error and returns an Image
        location = Location('01002')
        elementTree = ET.parse('test/test-forecast-data.xml')
        testWGSource = WeatherGovSource(location, Forecast.PARAM_RANGE_STEPS_DEFAULT, elementTree=elementTree)
        MockWeatherGovSource.return_value = testWGSource
        forecast = Forecast(location)
        image = Sticker(forecast).image
        self.assertEqual((126, 199), image.size)


        # @unittest.skip("tested by WeatherGovSourceTestCase, which has realistic data")
        # def testCalendarHeaderRow(self):
        # pass

        # @unittest.skip("tested by WeatherGovSourceTestCase, which has realistic data")
        # def testHoursAsCalendarRows(self):
        # pass
