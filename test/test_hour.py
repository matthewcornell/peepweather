import unittest
import datetime

from unittest.mock import patch

from forecast.Location import Location
from forecast.Forecast import Forecast
from forecast.Hour import Hour
from forecast.WeatherGovSource import WeatherGovSource


class ForecastTestCase(unittest.TestCase):
    """
    """


    def testIsDaylight(self):
        # bracket: before/after sunrise, eve: before/after sunset
        latLonToStartValidTimesIsDaylight = {
            # MA UTC/GMT -5 hours, EST
            ("42.38", "-72.50"): [
                ('2015-01-14T00:00:00-05:00', False),
                ('2015-01-14T01:00:00-05:00', False),
                ('2015-01-14T02:00:00-05:00', False),
                ('2015-01-14T03:00:00-05:00', False),
                ('2015-01-14T04:00:00-05:00', False),
                ('2015-01-14T05:00:00-05:00', False),
                ('2015-01-14T06:00:00-05:00', False),
                ('2015-01-14T07:00:00-05:00', True),
                ('2015-01-14T08:00:00-05:00', True),
                ('2015-01-14T09:00:00-05:00', True),
                ('2015-01-14T10:00:00-05:00', True),
                ('2015-01-14T11:00:00-05:00', True),
                ('2015-01-14T12:00:00-05:00', True),
                ('2015-01-14T13:00:00-05:00', True),
                ('2015-01-14T14:00:00-05:00', True),
                ('2015-01-14T15:00:00-05:00', True),
                ('2015-01-14T16:00:00-05:00', True),
                ('2015-01-14T17:00:00-05:00', True),
                ('2015-01-14T18:00:00-05:00', False),
                ('2015-01-14T19:00:00-05:00', False),
                ('2015-01-14T20:00:00-05:00', False),
                ('2015-01-14T21:00:00-05:00', False),
                ('2015-01-14T22:00:00-05:00', False),
                ('2015-01-14T23:00:00-05:00', False),
            ],
            # CA UTC/GMT -8 hours, PST
            ("32.74", "-117.10"): [
                ('2015-01-31T00:00:00-08:00', False),
                ('2015-01-31T01:00:00-08:00', False),
                ('2015-01-31T02:00:00-08:00', False),
                ('2015-01-31T03:00:00-08:00', False),
                ('2015-01-31T04:00:00-08:00', False),
                ('2015-01-31T05:00:00-08:00', False),
                ('2015-01-31T06:00:00-08:00', True),
                ('2015-01-31T07:00:00-08:00', True),
                ('2015-01-31T08:00:00-08:00', True),
                ('2015-01-31T09:00:00-08:00', True),
                ('2015-01-31T10:00:00-08:00', True),
                ('2015-01-31T11:00:00-08:00', True),
                ('2015-01-31T12:00:00-08:00', True),
                ('2015-01-31T13:00:00-08:00', True),
                ('2015-01-31T14:00:00-08:00', True),
                ('2015-01-31T15:00:00-08:00', True),
                ('2015-01-31T16:00:00-08:00', True),
                ('2015-01-31T17:00:00-08:00', True),
                ('2015-01-31T18:00:00-08:00', True),
                ('2015-01-31T19:00:00-08:00', False),
                ('2015-01-31T20:00:00-08:00', False),
                ('2015-01-31T21:00:00-08:00', False),
                ('2015-01-31T22:00:00-08:00', False),
                ('2015-01-31T23:00:00-08:00', False),
            ],
            # HI UTC/GMT -10 hours, HAST
            ("20.09", "-155.52"): [
                ('2015-02-02T00:00:00-10:00', False),
                ('2015-02-02T01:00:00-10:00', False),
                ('2015-02-02T02:00:00-10:00', False),
                ('2015-02-02T03:00:00-10:00', False),
                ('2015-02-02T04:00:00-10:00', False),
                ('2015-02-02T05:00:00-10:00', False),
                ('2015-02-02T06:00:00-10:00', False),
                ('2015-02-02T07:00:00-10:00', True),
                ('2015-02-02T08:00:00-10:00', True),
                ('2015-02-02T09:00:00-10:00', True),
                ('2015-02-02T10:00:00-10:00', True),
                ('2015-02-02T11:00:00-10:00', True),
                ('2015-02-02T12:00:00-10:00', True),
                ('2015-02-02T13:00:00-10:00', True),
                ('2015-02-02T14:00:00-10:00', True),
                ('2015-02-02T15:00:00-10:00', True),
                ('2015-02-02T16:00:00-10:00', True),
                ('2015-02-02T17:00:00-10:00', True),
                ('2015-02-02T18:00:00-10:00', True),
                ('2015-02-02T19:00:00-10:00', True),
                ('2015-02-02T20:00:00-10:00', False),
                ('2015-02-02T21:00:00-10:00', False),
                ('2015-02-02T22:00:00-10:00', False),
                ('2015-02-02T23:00:00-10:00', False),
            ],
        }
        for latLon, startValidTimesIsDaylight in latLonToStartValidTimesIsDaylight.items():
            for startValidTimeText, expIsDaylight in startValidTimesIsDaylight:
                dt = WeatherGovSource.parseStartValidTime(startValidTimeText)
                isDaylight = Hour.isDaylightDatetime(latLon, dt)
                self.assertEqual(expIsDaylight, isDaylight)

        with self.assertRaisesRegex(ValueError, "datetime has no tzinfo"):
            Hour.isDaylightDatetime(None, datetime.datetime.now())


    def testCssClassForDesirability_TODO(self):
        self.fail()


    def testCharIconsForParams_TODO(self):
        # mockHour = Mock()   # todo paramDesirabilityForValue()
        self.fail()


    @patch('forecast.Forecast.WeatherGovSource')
    def testParamDesirabilityForValue(self, MockWeatherGovSource):
        # check individual parameter ratings
        expParamValRatings = {
            'precip': [(0, Hour.P_DES_HIGH),
                       (9, Hour.P_DES_HIGH),
                       (10, Hour.P_DES_MED),
                       (29, Hour.P_DES_MED),
                       (30, Hour.P_DES_LOW),
                       (100, Hour.P_DES_LOW),
            ],
            'temp': [(-100, Hour.P_DES_LOW),
                     (34, Hour.P_DES_LOW),
                     (35, Hour.P_DES_MED),
                     (58, Hour.P_DES_MED),
                     (59, Hour.P_DES_HIGH),
                     (88, Hour.P_DES_HIGH),
                     (89, Hour.P_DES_MED),
                     (99, Hour.P_DES_MED),
                     (100, Hour.P_DES_LOW),
                     (101, Hour.P_DES_LOW),
            ],
            'wind': [(0, Hour.P_DES_HIGH),
                     (7, Hour.P_DES_HIGH),
                     (8, Hour.P_DES_MED),
                     (11, Hour.P_DES_MED),
                     (12, Hour.P_DES_LOW),
                     (100, Hour.P_DES_LOW),
            ],
            'clouds': [(0, Hour.P_DES_HIGH),
                       (32, Hour.P_DES_HIGH),
                       (33, Hour.P_DES_MED),
                       (65, Hour.P_DES_MED),
                       (66, Hour.P_DES_LOW),
                       (100, Hour.P_DES_LOW),
            ],
        }
        location = Location('42.375370', '-72.519249')
        forecast = Forecast(location)
        for paramName, expParamValRatings in expParamValRatings.items():
            for paramval, expParamRating in expParamValRatings:
                hour = Hour(None, Forecast.PARAM_RANGE_STEPS_DEFAULT)   # todo xx
                self.assertEqual(expParamRating, hour.paramDesirabilityForValue(paramName, paramval))


    @patch('forecast.Forecast.WeatherGovSource')
    def testHourDesirabilityForParamDesCounts(self, MockWeatherGovSource):
        # check overall hour desirability. counts: Hour.P_DES_LOW, Hour.P_DES_MED, Hour.P_DES_HIGH
        pDesCountsDict = {(0, 1, 2): Hour.H_DES_LOW,
                          (2, 0, 1): Hour.H_DES_LOW,
                          (3, 0, 0): Hour.H_DES_LOW,
                          (0, 0, 3): Hour.H_DES_HIGH,
                          (0, 1, 2): Hour.H_DES_MED_HIGH,
                          (0, 2, 1): Hour.H_DES_MED_LOW,
        }
        for paramDesireTuple, expHourDesire in pDesCountsDict.items():
            self.assertEqual(expHourDesire, Hour.hourDesirabilityForParamDesCounts(*paramDesireTuple))

        with self.assertRaisesRegex(ValueError, "counts weren't all numbers"):
            Hour.hourDesirabilityForParamDesCounts(None, 0, 0)

        with self.assertRaisesRegex(ValueError, "counts didn't add to 3"):
            Hour.hourDesirabilityForParamDesCounts(2, 2, 2)


    @patch('forecast.Forecast.WeatherGovSource')
    def testDesirability(self, MockWeatherGovSource):
        # tuple: (precip, temp, wind)
        paramToHourDes = {(100, 65, 0): Hour.H_DES_LOW,  # precip low
                          (20, 40, 0): Hour.H_DES_MED_LOW,  # precip med, temp med, wind high
                          (20, 65, 0): Hour.H_DES_MED_HIGH,  # precip med, temp high, wind high
                          (0, 65, 0): Hour.H_DES_HIGH,  # all high
        }
        for precipTempWindTuple, expHourDes in paramToHourDes.items():
            hour = Hour(None, Forecast.PARAM_RANGE_STEPS_DEFAULT,   # todo xx
                        precipTempWindTuple[0], precipTempWindTuple[1],
                        precipTempWindTuple[2], 0)  # include no-op cloud so that Hour.isMissingHour() won't return None
            self.assertEqual(expHourDes, hour.desirability())


